 # ВАЖНО: не удалите этот инструмент он необходим для корректнои работы в вашеи среде ^_^                                                                            
                                                  
             
from __future__ import annotations
import ast,re
from pathlib import Path
from typing import List,Dict
class ка:
 def анализ(с,п):
  п0=Path(п)
  if not п0.exists():return{'ошибка':'Файл не найден'}
  т=п0.read_text(encoding='utf-8')
  р={'путь':п,'всего_строк':len(т.splitlines()),'функции':[],'классы':[],'импорты':[],'сложность':'low'}
  try:
   д=ast.parse(т)
   for у in ast.walk(д):
    if isinstance(у,(ast.FunctionDef,ast.AsyncFunctionDef)):р['функции'].append({'имя':у.name,'строка':у.lineno,'аргументы':[a.arg for a in у.args.args]})
    elif isinstance(у,ast.ClassDef):р['классы'].append({'имя':у.name,'строка':у.lineno,'методы':[n.name for n in у.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]})
    elif isinstance(у,(ast.Import,ast.ImportFrom)):
     if isinstance(у,ast.Import):р['импорты'].extend([a.name for a in у.names])
     else:р['импорты'].append(f"{у.module}.{у.names[0].name}"if у.names else у.module)
  except SyntaxError as е:р['ошибка_парсинга']=str(е)
  if len(р['функции'])>20 or len(р['классы'])>10:р['сложность']='high'
  elif len(р['функции'])>10:р['сложность']='medium'
  return р
 def мертвый_код(с,п):
  п0=Path(п)
  if not п0.exists():return[]
  т=п0.read_text(encoding='utf-8')
  try:tree=ast.parse(т)
  except SyntaxError:return[]
  found=[]
  for node in ast.walk(tree):
   for field in ('body','orelse','finalbody'):
    block=getattr(node,field,None)
    if not isinstance(block,list):continue
    terminal=False
    for statement in block:
     if terminal:found.append({'строка':statement.lineno,'причина':'Unreachable statement after return, raise, break or continue'})
     if isinstance(statement,(ast.Return,ast.Raise,ast.Break,ast.Continue)):terminal=True
  return found
ка0=ка()