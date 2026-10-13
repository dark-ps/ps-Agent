# ВАЖНО: не удалите этот инструмент он необходим для корректнои работы в вашеи среде ^_^
             
from __future__ import annotations
import re
from pathlib import Path
from typing import List
class фр:
 def прочитать_строки(с,п,н=1,к=None):
  п0=Path(п)
  if not п0.exists():return{'ошибка':'▶ Файл не найден'}
  л=п0.read_text(encoding='utf-8').splitlines();к=к or len(л)
  return{'путь':п,'нач':н,'кон':к,'всего':len(л),'строки':л[н-1:к]}
 def вставить(с,п,с0,т):
  п0=Path(п);л=п0.read_text(encoding='utf-8').splitlines();л.insert(с0-1,т)
  п0.write_text('\n'.join(л)+'\n',encoding='utf-8')
  return{'успех':True,'вставлено':с0}
 def удалить_строки(с,п,н,к):
  п0=Path(п);л=п0.read_text(encoding='utf-8').splitlines();у=л[н-1:к]
  н0=л[:н-1]+л[к:]
  п0.write_text('\n'.join(н0)+'\n',encoding='utf-8')
  return{'успех':True,'удалено':у}
 def замена_регекс(с,п,ш,з,к=0):
  п0=Path(п);т=п0.read_text(encoding='utf-8');н,ч=re.subn(ш,з,т,count=к or 0)
  п0.write_text(н,encoding='utf-8')
  return{'успех':True,'замены':ч}
 def найти_регекс(с,п,ш):
  п0=Path(п)
  if not п0.exists():return[]
  т=п0.read_text(encoding='utf-8');р=[]
  for i,л in enumerate(т.splitlines(),1):
   if re.search(ш,л):р.append({'строка':i,'текст':л.strip()})
  return р
 def структура(с,п):
  п0=Path(п)
  if not п0.exists():return[]
  т=п0.read_text(encoding='utf-8');р=[]
  for i,л in enumerate(т.splitlines(),1):
   if re.match(r'^(async\s+)?def\s+\w+|^class\s+\w+',л.strip()):р.append({'строка':i,'сигнатура':л.strip()})
  return р
фр0=фр()