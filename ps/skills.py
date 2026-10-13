# новый файл 

from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

class PromptSkill:
    def __init__(self, path: Path, meta: Optional[dict] = None):
        self.path = path
        self.name = path.stem
        self.description = ""
        self.version = "1.0"
        if meta:
            self.name = str(meta.get("name") or self.name)
            self.description = str(meta.get("description") or "")
            self.version = str(meta.get("version") or "1.0")
        self._load_meta()

    def _load_meta(self):
        try:
            text = self.path.read_text(encoding="utf-8", errors="replace")
            if text.startswith("---"):
                end = text.find("\n---", 3)
                if end >= 0:
                    meta = text[3:end]
                    for line in meta.splitlines():
                        if ":" not in line:
                            continue
                        k, v = line.split(":", 1)
                        k, v = k.strip(), v.strip()
                        if k == "name":
                            self.name = v
                        elif k == "description" and not self.description:
                            self.description = v
                        elif k == "version":
                            self.version = v
            if not self.description:
                for line in text.splitlines():
                    line = line.strip().lstrip("#").strip()
                    if line and not line.startswith("---"):
                        self.description = line[:220]
                        break
        except Exception:
            pass

    def read(self, max_chars: int = 24000) -> str:
        text = self.path.read_text(encoding="utf-8", errors="replace")
        return text if len(text) <= max_chars else text[:max_chars] + \
            "\n\n[SKILL TRUNCATED — load supporting resources if needed]"


class PromptSkillRegistry:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.skills_dir = self.root / "ps" / "prompts" / "skills"
        self.catalog_path = self.skills_dir / "catalog.json"
        self.skills: Dict[str, PromptSkill] = {}
        self.aliases: Dict[str, str] = {}
        self.reload()

    def reload(self):
        self.skills.clear()
        self.aliases.clear()
        if not self.skills_dir.exists():
            return
        catalog = {}
        try:
            if self.catalog_path.is_file():
                raw = json.loads(self.catalog_path.read_text(encoding="utf-8"))
                for item in raw.get("skills", []):
                    if isinstance(item, dict) and item.get("name"):
                        catalog[str(item["name"]).lower()] = item
        except Exception:
            catalog = {}

        for p in sorted(self.skills_dir.glob("*.md")):
            if p.name.startswith(".") or p.name.lower() == "readme.md":
                continue
            try:
                meta = catalog.get(p.stem.lower())
                skill = PromptSkill(p, meta=meta)
                self.skills[skill.name] = skill
                key = skill.name.lower()
                self.aliases[key] = skill.name
                self.aliases[p.stem.lower()] = skill.name
                self.aliases[p.name.lower()] = skill.name
            except Exception:
                continue

    def catalog(self, max_items: int = 1200, max_desc: int = 100, query: str = "") -> str:
        rows = []
        terms={term for term in re.findall(r"\w+",query.lower()) if len(term)>2}
        def rank(skill):
            text=(skill.name+' '+skill.description).lower()
            return (-sum(term in text for term in terms),skill.name.lower())
        selected=sorted(self.skills.values(),key=rank)[:max_items]
        for skill in selected:
            desc = re.sub(r"\s+", " ", skill.description).strip()[:max_desc]
            rows.append(f"  - {skill.name}: {desc}")
        if len(self.skills)>len(selected):rows.append(f"  {len(self.skills)-len(selected)} additional skills remain installed; use the skills command for the complete catalog.")
        return "\n".join(rows)

    def catalog_json(self) -> list[dict]:
        return [
            {"name": s.name, "description": re.sub(r"\s+", " ", s.description).strip()[:220],
             "version": s.version}
            for s in sorted(self.skills.values(), key=lambda x: x.name.lower())
        ]

    def get(self, name: str) -> Optional[PromptSkill]:
        key = (name or "").strip().lower()
        if key.startswith("/"):
            key = key[1:]
        canonical = self.aliases.get(key, key)
        skill = self.skills.get(canonical)
        if skill:
            return skill
        for k, v in self.skills.items():
            if k.lower() == key:
                return v
        return None

    def load(self, name: str, max_chars: int = 24000) -> Optional[str]:
        skill = self.get(name)
        return skill.read(max_chars=max_chars) if skill else None

    def activate(self, name: str, max_chars: int = 24000) -> dict:
        skill = self.get(name)
        if not skill:
            return {
                "ok": False,
                "error": f"Skill not found: {name}",
                "available": [s.name for s in sorted(self.skills.values(), key=lambda x: x.name)[:50]],
            }
        return {
            "ok": True,
            "skill": skill.name,
            "path": str(skill.path),
            "description": skill.description,
            "instructions": skill.read(max_chars=max_chars),
        }

    def match(self, query: str, limit: int = 8) -> List[dict]:
        q = set(re.findall(r"[a-z0-9_-]+", (query or "").lower()))
        scored = []
        for s in self.skills.values():
            words = set(re.findall(r"[a-z0-9_-]+", (s.name + " " + s.description).lower()))
            score = len(q & words)
            if score:
                scored.append((score, s))
        scored.sort(key=lambda x: (-x[0], x[1].name.lower()))
        return [
            {"name": s.name, "description": s.description, "score": score}
            for score, s in scored[:limit]
        ]


def load_skill(root, name, max_chars=24000):
    return PromptSkillRegistry(root).load(name, max_chars=max_chars)
 
# данный проект был разработан: T.me/sii_3
