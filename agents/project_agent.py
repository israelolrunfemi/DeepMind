"""ProjectAgent scaffolds complete multi-file Python projects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agents.base_agent import BaseAgent
from config import MAX_PROJECT_FILES, WORKSPACE_DIR
from tools.registry import call_tool, get_tool_descriptions
from utils.parser import extract_code_block, extract_json


class ProjectAgent(BaseAgent):
    """Build complete Python projects from a high-level goal."""

    SYSTEM_PROMPT = (
        "You are a senior Python architect. You build complete, production-quality Python projects. "
        "All files you write must be consistent with each other. Imports must resolve, models must "
        "match across files. Output only valid Python code in code blocks. No explanations outside "
        "code blocks."
    )

    PLAN_PROMPT = (
        "Create a JSON project plan only. Prefer the Python standard library unless dependencies are "
        "truly required. The entry point must run without interactive input. Include at most "
        f"{MAX_PROJECT_FILES} files. Available tools:\n{{tools}}\n\nGoal: {{goal}}\n\n"
        "Required JSON shape: {{\"project_name\":\"name\",\"description\":\"...\",\"files\":[{{\"path\":\"main.py\","
        "\"description\":\"...\"}}],\"dependencies\":[],\"entry_point\":\"main.py\",\"run_command\":\"python main.py\"}}"
    )

    async def run(self, goal: str, workspace: str = WORKSPACE_DIR) -> dict[str, Any]:
        """Build a complete project from a goal string."""

        self.emit_start({"goal": goal, "workspace": workspace})
        project_name = "project"
        project_path = ""
        files_created: list[str] = []
        dependencies_installed: list[str] = []

        try:
            plan_response = await self.llm.complete(
                system_prompt="You produce only valid JSON project plans.",
                user_prompt=self.PLAN_PROMPT.format(tools=get_tool_descriptions(), goal=goal),
            )
            plan = extract_json(plan_response)
            project_name = self._safe_name(str(plan.get("project_name") or "devmind_project"))
            project_path = str(Path(workspace) / project_name)
            files = self._plan_files(plan)
            dependencies = self._plan_dependencies(plan)
            entry_point = str(plan.get("entry_point") or "main.py")

            create_result = await self._call_tool("create_directory", path=project_path)
            if create_result.get("status") != "success":
                return self._failure(project_name, project_path, files_created, dependencies_installed, {}, create_result)

            for dependency in dependencies:
                install_result = await self._call_tool("install_package", name=dependency)
                if install_result.get("status") == "success":
                    dependencies_installed.append(dependency)

            plan_json = json.dumps(plan, indent=2)
            for file_spec in files:
                relative_path = self._safe_relative_path(str(file_spec["path"]))
                target_path = str(Path(project_path) / relative_path)
                code_response = await self.llm.complete(
                    system_prompt=self.SYSTEM_PROMPT,
                    user_prompt=(
                        f"Project goal:\n{goal}\n\nFull project plan:\n{plan_json}\n\n"
                        f"Write the complete content for {relative_path}. "
                        f"File purpose: {file_spec.get('description', '')}"
                    ),
                )
                content = extract_code_block(code_response)
                write_result = await self._call_tool("write_file", path=target_path, content=content)
                if write_result.get("status") != "success":
                    return self._failure(project_name, project_path, files_created, dependencies_installed, {}, write_result)
                files_created.append(target_path)

            run_result = await self._run_entry_point(project_path, entry_point)
            tree_result = await self._call_tool("get_file_tree", root=project_path, max_depth=3)
            file_tree = tree_result.get("tree", {}) if tree_result.get("status") == "success" else {}
            success = run_result.get("status") == "success"
            result = {
                "success": success,
                "project_name": project_name,
                "project_path": project_path,
                "files_created": files_created,
                "dependencies_installed": dependencies_installed,
                "run_output": run_result.get("output") or run_result.get("result"),
                "file_tree": file_tree,
                "error": None if success else str(run_result.get("error", "Project run failed")),
            }
            self.emit_complete({"project_name": project_name, "success": success})
            return result
        except (RuntimeError, ValueError, TypeError, KeyError) as exc:
            self.emit_error(str(exc))
            return {
                "success": False,
                "project_name": project_name,
                "project_path": project_path,
                "files_created": files_created,
                "dependencies_installed": dependencies_installed,
                "run_output": None,
                "file_tree": {},
                "error": str(exc),
            }

    async def _call_tool(self, name: str, **kwargs: Any) -> dict[str, Any]:
        self.emit_tool_call(name, kwargs)
        result = await call_tool(name, **kwargs)
        self.emit_tool_result(name, result)
        return result

    async def _run_entry_point(self, project_path: str, entry_point: str) -> dict[str, Any]:
        entry_path = Path(project_path) / self._safe_relative_path(entry_point)
        if not entry_path.exists():
            return {"status": "error", "error": f"Entry point not found: {entry_path}"}
        bootstrap = (
            "import runpy\n"
            "import sys\n"
            f"sys.path.insert(0, {str(Path(project_path).resolve())!r})\n"
            f"runpy.run_path({str(entry_path.resolve())!r}, run_name='__main__')\n"
        )
        return await self._call_tool("run_code", code=bootstrap)

    def _failure(
        self,
        project_name: str,
        project_path: str,
        files_created: list[str],
        dependencies_installed: list[str],
        file_tree: dict[str, Any],
        tool_result: dict[str, Any],
    ) -> dict[str, Any]:
        error = str(tool_result.get("error", "Tool call failed"))
        self.emit_error(error)
        return {
            "success": False,
            "project_name": project_name,
            "project_path": project_path,
            "files_created": files_created,
            "dependencies_installed": dependencies_installed,
            "run_output": None,
            "file_tree": file_tree,
            "error": error,
        }

    def _plan_files(self, plan: dict[str, Any]) -> list[dict[str, Any]]:
        files = plan.get("files", [])
        if not isinstance(files, list) or not files:
            raise ValueError("Project plan did not include files")
        cleaned: list[dict[str, Any]] = []
        for item in files[:MAX_PROJECT_FILES]:
            if isinstance(item, dict) and item.get("path"):
                cleaned.append(item)
        if not cleaned:
            raise ValueError("Project plan files were invalid")
        return cleaned

    def _plan_dependencies(self, plan: dict[str, Any]) -> list[str]:
        dependencies = plan.get("dependencies", [])
        if not isinstance(dependencies, list):
            return []
        return [str(dependency) for dependency in dependencies if str(dependency).strip()]

    def _safe_name(self, value: str) -> str:
        allowed = [character.lower() if character.isalnum() else "-" for character in value.strip()]
        name = "".join(allowed).strip("-")
        return name or "devmind-project"

    def _safe_relative_path(self, value: str) -> str:
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Unsafe project file path: {value}")
        return str(path)
