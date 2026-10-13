from __future__ import annotations

from pathlib import Path as п
from typing import List as с


_п = "prompts"
_и = "identity.md"
_ФРАГМ = "fragments"
_НАВЫКИ = "skills"


class р:
    def __init__(self, к: п, л=None):
        self.к = п(к)
        self.п = self.к / _п
        self.л = л
        self.ф: с[п] = self._н()
        self.и = self._ч(self.к.parent / _и)

    def х(self, л):
        self.л = л

    def _ч(self, ф: п) -> str:
        try:
            if ф.is_file():
                return ф.read_text(encoding="utf-8", errors="replace").strip()
        except Exception:
            pass
        return ""

    def _н(self) -> с[п]:
        if not self.п.exists():
            return []

        return [
            ф
            for ф in sorted(
                х for х in self.п.rglob("*")
                if х.is_file()
                and (
                    х.suffix in (".md", ".dark", ".ps")
                    or х.name.endswith("@sii_3")
                )
            )
            if not ф.name.startswith(".")
            and _ФРАГМ not in ф.relative_to(self.п).parts
            # Prompt skills have their own progressive-disclosure registry.
            # Never ingest SKILL.md files into the base prompt: the model sees
            # only their short catalog entry and explicitly activates the full
            # instructions through TOOL skill when needed.
            and _НАВЫКИ not in ф.relative_to(self.п).parts
        ]

    @staticmethod
    def _с(т: str, м: int = 30) -> str:
        т = т or ""
        с = т.strip().splitlines()
        if len(с) <= м:
            return т
        ч = с[:м]
        ч.append(f"... ({len(с) - м} more tools available via list command)")
        return "\n".join(ч)

    @staticmethod
    def _б(м, н, в, д, р) -> str:
        с = []
        с.append("**MCP TOOLS:**")
        if м:
            с.append('Use TOOL: {"tool":"mcp","mcp_tool":"<tool_name>","arguments":{...}} only for the connected MCP tools listed here.')
            с.append(м)
        else:
            с.append('No MCP tools are connected. Native interpreter functions in LOADED-TOOLS are separate: call them as TOOL: {"tool":"module.function","arguments":{...}}, never as MCP tools.')
        с.append("")
        с.append("**SKILLS:**")
        с.append('Choose only the relevant skill(s). Use TOOL: {"tool":"skill","skill_name":"<skill_name>","arguments":{...}}; call it again for another skill when needed. Full instructions are injected only after activation. MANDATORY: for requests to build or modify a website, web app, frontend, landing page, or UI, activate the most relevant web skill (prefer website-builder for a complete site, otherwise web-ui/frontend-engineering) before taking action; do not skip skill activation.')
        с.append(н or "")
        с.append("")
        с.append("**MEMORY CONTEXT:**")
        с.append(в or "")
        с.append("")
        с.append("**PROJECT DATABASE MEMORY (.database-darkps):**")
        с.append(д or "")
        с.append("")
        с.append("**WORKSPACE:**")
        с.append(р or "")
        return "\n".join(с)

    def а(
        self,
        у,
        workspace_info: str = "",
        memory_context: str = "",
        tools_list: str = "",
        mcp_info: str = "",
        skills_info: str = "",
        plan_text: str = "",
        db_context: str = "",
        animation_styles: str = "",
        сес=None,
        ткн=None,
        мдл=None,
    ) -> str:
        с = []

        if self.и:
            с.append(self.и)

        for ф in self.ф:
            х = self._ч(ф)
            if not х:
                continue
            if ф.name == "@sii_3" and animation_styles:
                х = х.replace("{стили_список}", animation_styles)
            с.append(х)

        б = self._б(
            м=mcp_info,
            н=skills_info,
            в=memory_context,
            д=db_context,
            р=workspace_info,
        )

        if б.strip():
            с.append(б)

        if plan_text.strip():
            с.append(f"\n----------PROJECT-PLAN----------\n\n{plan_text}")

        if tools_list.strip():
            с.append(f"\n----------LOADED-TOOLS----------\n\n{self._с(tools_list)}")

        return "\n\n".join(х.strip() for х in с if х and х.strip())

    def е(
        self,
        у,
        сес=None,
        ткн=None,
        мдл=None,
    ):
        ч = len(self.и or "")
        с = [_и] if self.и else []

        for ф in self.ф:
            с.append(ф.name)
            ч += len(self._ч(ф))

        return {
            "sections": с,
            "count": len(с),
            "estimated_chars": ч,
        }


def dark(к, л=None):
    return р(к, л)


def фрагмент(ном: str, корень=None) -> str:
    к = п(корень) if корень else п(__file__).resolve().parent
    ф = к / _п / _ФРАГМ / f"{ном}.dark"
    try:
        if ф.is_file():
            return ф.read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        pass
    return ""
    
# данный проект был разработан: T.me/sii_3
