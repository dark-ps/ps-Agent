# ВАЖНО: не удалите этот инструмент он необходим для корректнои работы в вашеи среде ^_^                   
             
from __future__ import annotations
import re
class лд:
 _ш={'arabic':re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'),'russian':re.compile(r'[\u0400-\u04FF\u0500-\u052F]'),'chinese':re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]'),'japanese':re.compile(r'[\u3040-\u309F\u30A0-\u30FF]'),'korean':re.compile(r'[\uAC00-\uD7AF\u1100-\u11FF]'),'hebrew':re.compile(r'[\u0590-\u05FF]'),'greek':re.compile(r'[\u0370-\u03FF]'),'thai':re.compile(r'[\u0E00-\u0E7F]')}
 def определить(с,т):
  if not т:return'en'
  for я,ш in с._ш.items():
   if ш.search(т):return я
  if re.search(r'[a-zA-Z]',т):return'en'
  return'unknown'
 def подсказка(с,т):
  я=с.определить(т)
  д={'arabic':'Пользователь говорит на арабском. Отвечай на арабском.','russian':'Пользователь пишет по-русски. Отвечай на русском.','chinese':'Пользователь использует китайский. Отвечай на китайском.','japanese':'Пользователь использует японский. Отвечай на японском.','korean':'Пользователь использует корейский. Отвечай на корейском.','hebrew':'Пользователь пишет на иврите. Отвечай на иврите.','english':'Пользователь пишет на английском. Отвечай на английском.'}
  return д.get(я,д['english'])
лд0=лд()