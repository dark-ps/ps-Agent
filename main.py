# - @2026 | Version 4.0
# - Created By: T.me/sii_3
# - Mr Dark
# ~ Agent DarkPs Official [>_]

from __future__ import annotations

скорость = 0.005 # скорость печати логотипа :|


#–––––––––––––––––––––––––––––––––#
# БАЗА ДАННЫХ СО ЗНАЧЕНИЕМ "True"    
# ОНО НЕ БУДЕТ УДАЛЕНО "False"         
# ПРИ КАЖДОИ ОПЕРАЦИИ ..              
      # ➘                                   
database=True                               
#––––––––––––––––––––––––––––––––#

# вы можете добавить свой собственныи логотип поддерживаются разные цвета просто скопируите и вставьте ➜ "логотип.md"

from pathlib import Path
from core.проверка import проверка
проверка(Path(__file__).resolve().parent)
if database:
    import shutil
    shutil.rmtree(Path.home() / ".darkps", ignore_errors=True)
from ps.dark import *
from interpreter import пуск as интер_пуск
import asyncio,re
import sys

with open(Path(__file__).resolve().parent / "логотип.md", "r", encoding="utf-8") as f:
    л = f.read()
    
ят = True
def цв(ц):
    ц = ц.lstrip("#")
    р, г, б = int(ц[0:2], 16), int(ц[2:4], 16), int(ц[4:6], 16)
    return f"\033[38;2;{р};{г};{б}m"
def чист(т):
    т = re.sub(r"<[^>]+>", "", т)
    т = re.sub(r"\[/?(font|size)[^\]]*\]", "", т)
    return т
async def д():
    ч = чист(л)
    ш = re.compile(r"#[0-9a-fA-F]{6}")
    строки = ч.splitlines()
    размер = max(1, len(строки) // 20)
    текущий_цвет = None
    for i in range(0, len(строки), размер):
        блок = строки[i:i + размер]
        for стр in блок:
            п = 0
            for м in ш.finditer(стр):
                н, к = м.span()
                if н > п:
                    текст = стр[п:н]
                    if ят and текущий_цвет:
                        print(
                            f"{цв(текущий_цвет)}{текст}",
                            end="",
                            flush=True
                        )
                    else:
                        print(
                            текст,
                            end="",
                            flush=True
                        )
                текущий_цвет = м.group()
                п = к
            остаток = стр[п:]
            if ят and текущий_цвет:
                print(
                    f"{цв(текущий_цвет)}{остаток}\033[0m",
                    flush=True
                )
            else:
                print(
                    остаток,
                    flush=True
                )
        await asyncio.sleep(
            скорость * max(1, размер / 10)
        )
if __name__ == '__main__':
    asyncio.run(д())
    print()
    try:
        from ps.серв import бан
        бан()
    except Exception:
        pass
    print()
    try:
        from core.режим import пуск as режим_пуск
        режим_пуск()
    except Exception:
        pass
    интер_пуск()
    глв()
    
# - By: T.me/sii_3
