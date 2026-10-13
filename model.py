from __future__ import annotations

import os
from dataclasses import dataclass, field

м = "qwen7b"  # модель по умолчанию :|

мс = [
# как добавить модели? :\\
# вот так их и нужно добавлять шлюха:
#  ↘
#    ↘
   # ('gpt-5.6-luna', 'darkps'), # - darkps.py
    ('qwen7b', 'free_ai'), # - free_ai.py
    ('glm-4.7-flash', 'Cloudflare'), # - Cloudflare.py
    ('glm-5.2', 'Cloudflare'), # - Cloudflare.py
   # ('gemini-3.5-flash', 'google'), # - google.py
   # ('kimi-k3', 'kimi'), # - kimi.py
   # ('qwen-3.8-max', 'qwenai'), # - qwenai.py
   # ('deepseek-v4-flash', 'deepseek'), # deepseek.py
   # ('halagpt-large', 'fanuonai'), # - fanuonai.py   
   # ('claude-5.1-fable', 'darkps'), # darkps.py
   # ('gpt-6-astra', 'darkps'), # - darkps.py
]


def тм() -> str:
    return os.getenv('DarkPs_MODEL', м)

@dataclass
class Модель:
    имя: str
    ссылка: str
    подсказка: str
    оперативка: dict = field(default_factory=dict)
    видеопамять: dict = field(default_factory=dict)

# Локальные модели "LOCALY" 
# вы можете добавлять/удалять 
# ↘
#   ↘
мо = [

    Модель(
        имя='iceAI', # имя 
        ссылка='bartowski/darkps_ice-AI-GGUF', # склад 
        подсказка='\\n\\n', # ненужный
    ),

    Модель(
        имя='deepseek-v4-flash',
        ссылка='ivanfioravanti/deepseek-v4-gguf',
        подсказка='\\n\\n',
    ),

    Модель(
        имя='qwen3.6-35b',
        ссылка='mudler/Qwen3.6-35B-A3B-NVFP4-GGUF',
        подсказка='\\n\\n',
    ),

    Модель(
        имя='DeepSeek-r1',
        ссылка='lmstudio-community/DeepSeek-R1-Distill-Qwen-32B-GGUF', # разум: Qwen-32b
        подсказка='\\n\\n',
    ),

    Модель(
        имя='DeepSeek-v3',
        ссылка='gghfez/DeepSeek-V3-0324-Opus3-Styletune-GGUF', # разум: Opus 3
        подсказка='\\n\\n',
    ),

]


def чит(имя: str, ссылка: str, подсказка: str = '\\n\\n',
                     оперативка: dict | None = None,
                     видеопамять: dict | None = None) -> Модель:
    новая = Модель(
        имя=имя,
        ссылка=ссылка,
        подсказка=подсказка,
        оперативка=оперативка or {},
        видеопамять=видеопамять or {},
    )
    мо.append(новая)
    return новая


def чвт(имя: str) -> bool:
    for i, м0 in enumerate(мо):
        if м0.имя == имя:
            del мо[i]
            return True
    return False


# - By: T.me/sii_3
