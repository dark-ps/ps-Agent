# ВАЖНО: не удалите этот инструмент он необходим для корректнои работы в вашеи среде ^_^

from __future__ import annotations
from typing import Dict,List,Callable,Any
from dataclasses import dataclass
@dataclass
class н:
 имя:str
 описание:str
 категория:str
 нужна_аутентификация:bool
 сервис:str
 запасной:str
 обработчик:Callable
class нр:
 def __init__(с):с.н={}
 def регистрация(с,н0):с.н[н0.имя]=н0
 def список(с,к=''):
  э=list(с.н.values())
  if к:э=[e for e in э if e.категория==к]
  return[{'имя':e.имя,'описание':e.описание,'категория':e.категория,'нужна_аутентификация':e.нужна_аутентификация,'сервис':e.сервис,'запасной':e.запасной}for e in э]
 def статус(с):
  л=[f'➡ Навыки:{len(с.н)} ready >_']
  п={}
  for e in с.н.values():п.setdefault(e.категория,[]).append(e.имя)
  for к,и in sorted(п.items()):л.append(f'  [{к}] {", ".join(и)}')
  return'\n'.join(л)
 def получить(с,и):return с.н.get(и)
нр0=нр()