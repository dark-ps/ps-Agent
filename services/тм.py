# ВАЖНО: не удалите этот инструмент он необходим для корректнои работы в вашеи среде ^_^

from __future__ import annotations
_J='нужен_проект'
_I='область'
_H='есть'
_G='scope'
_F='header'
_E='url'
_D='keys'
_C='project'
_B=False
_A='валид'
import os
from pathlib import Path
import requests
_ENV=Path.home()/'.darkps'/'.env'
_SERVICES={'github':{_D:['GITHUB_TOKEN','GH_TOKEN'],_E:'https://api.github.com/user',_F:'token {}',_G:'repo, gist',_C:True},'huggingface':{_D:['HF_TOKEN','HUGGINGFACE_TOKEN'],_E:'https://huggingface.co/api/whoami-v2',_F:'Bearer {}',_G:'read repos',_C:_B}}
class тм:
	def __init__(A):A._к={}
	def _ч(E):
		B={}
		if _ENV.exists():
			for A in _ENV.read_text(encoding='utf-8',errors='replace').splitlines():
				A=A.strip()
				if A and not A.startswith('#')and'='in A:C,D=A.split('=',1);B[C.strip()]=D.strip().strip('"').strip("'")
		return B
	def проверить(O,св):
		N='****';K='Authorization';G='сообщ';E=св;F=_SERVICES.get(E,{});P=F.get(_D,[]);Q=O._ч();A='';I='none'
		for L in P:
			C=os.getenv(L,'')
			if C:A=C;I='env';break
			C=Q.get(L,'')
			if C:A=C;I='env_file';break
		B={'сервис':E,_H:bool(A),'источник':I,'значение':N+A[-4:]if len(A)>4 else N if A else'',_A:_B,_I:F.get(_G,''),_J:F.get(_C,_B),G:''}
		if not A:B[G]=f"ⓘ – Нет токена для {E}.";return B
		M=F.get(_E)
		if M:
			try:
				D=F[_F].format(A)
				if':'in D:R,C=D.split(':',1);H={R.strip():C.strip()}
				elif D.startswith('Bearer '):H={K:D.strip()}
				elif D.startswith('token '):H={K:D.strip()}
				else:H={K:D.strip()}
				J=requests.get(M,headers=H,timeout=10);B[_A]=J.status_code==200;B[G]=f"Токен {E} валиден."if J.status_code==200 else f"Статус {J.status_code}."
			except Exception as S:B[G]=f"Ошибка проверки: {S}"
		else:B[_A]=True;B[G]=f"Токен {E} существует."
		return B
	def список(A):return[A.проверить(B)for B in _SERVICES.keys()]
	def отчет(D,*F,**G):
		B=['— Статус токенов:']
		for C in _SERVICES.keys():
			A=D.проверить(C);E='✓'if A[_A]else'ⓘ 'if A[_H]else'✘';B.append(f"  {E} {C}: есть={A[_H]}, валид={A[_A]}, область={A[_I]}")
			if A[_J]:B.append('      ➥ Может требовать ключ проекта')
		return'\n'.join(B)
	def нужен_ли(A,св,проект=''):
		B=_SERVICES.get(св,{})
		if not B.get(_C,_B):return _B
		return not A.проверить(св)[_A]
тм0=тм()