from __future__ import annotations

# ВАЖНО: не удалите этот инструмент он необходим для корректнои работы в вашеи среде ^_^ [ данныи текст адресован пользователю не программе ]

# Usage (via TOOL: run_file, or directly):
# python huggingface.py <action> <query-or-id> [depth] [extra]
# "python" – "python3 -->> APPLIES TO THE SYSTEM
# HuggingFace toolkit for searching, inspecting, and accessing HuggingFace resources.
#
# Supported actions:
# search-models     – Search HuggingFace models by name or topic.
# search-datasets   – Search HuggingFace datasets by name or topic.
# search-spaces     – Search HuggingFace Spaces applications.
# info              – Get detailed information about a model/dataset/space.
# file              – Read a file from a HuggingFace repository.
#
# Depth levels:
# fast     – Quick results with minimal details.
# medium   – More results and metadata (default).
# deep     – Maximum details, model cards, and repository files when available.
#
# Token:
# Public resources work without a token.
# Private or gated HuggingFace resources require HF_TOKEN or HUGGINGFACE_TOKEN.
#
# Use this tool when you need AI models, datasets, Spaces, repository files,
# model details, downloads, likes, tags, pipeline information, or HuggingFace links.

_e='Private'
_d='pipeline_tag'
_c='Authorization'
_b='HUGGINGFACE_TOKEN='
_a='HF_TOKEN='
_Z='replace'
_Y='.darkps'
_X='tags'
_W='unknown'
_V='direction'
_U='sort'
_T='limit'
_S='search'
_R='токен'
_Q='space'
_P='utf-8'
_O='сообщ'
_N='gated'
_M='dataset'
_L='likes'
_K='downloads'
_J='fast'
_I='валид'
_H='нужен'
_G='private'
_F=False
_E='model'
_D='\n'
_C='deep'
_B='medium'
_A=True
import os
from pathlib import Path
import requests
_API='https://huggingface.co/api'
_WEB='https://huggingface.co'
def _гт():
	B=os.getenv('HF_TOKEN','')or os.getenv('HUGGINGFACE_TOKEN','')
	if B:return B
	C=Path.home()/_Y/'.env'
	if C.exists():
		for A in C.read_text(encoding=_P,errors=_Z).splitlines():
			if A.startswith(_a)or A.startswith(_b):return A.split('=',1)[1].strip().strip('"').strip("'")
	return''
def _сгт(token):
	D=token;E=Path.home()/_Y;E.mkdir(parents=_A,exist_ok=_A);B=E/'.env';G=B.read_text(encoding=_P,errors=_Z).splitlines()if B.exists()else[];A=[];F=_F
	for C in G:
		if C.startswith(_a)or C.startswith(_b):A.append(f"HF_TOKEN={D}");F=_A
		else:A.append(C)
	if not F:A.append(f"HF_TOKEN={D}")
	B.write_text(_D.join(A)+_D,encoding=_P)
def _валиден(token):
	try:A=requests.get(f"{_API}/whoami-v2",headers={_c:f"Bearer {token}"},timeout=10);return A.status_code==200
	except Exception:return _F
def _заголовки(token=''):
	A=token;B={'Accept':'application/json','User-Agent':'DarkPs-Agent/1.0'}
	if A:B[_c]=f"Bearer {A}"
	return B
def _требует_токен_hf(kind,repo_id):
	A=repo_id;D={_E:f"models/{A}",_M:f"datasets/{A}",_Q:f"spaces/{A}"}.get(kind,f"models/{A}")
	try:
		B=requests.get(f"{_API}/{D}",headers=_заголовки(),timeout=10)
		if B.status_code==200:C=B.json();return bool(C.get(_N)or C.get(_G))
		return B.status_code in{401,403,404}
	except Exception:return _F
def _токен_если_нужно(kind='',repo_id=''):
	C=repo_id;B='есть';A=_гт()
	if C and not _требует_токен_hf(kind,C):return{_H:_F,B:bool(A),_I:_A,_O:'Публичный ресурс, токен не нужен.'}
	if A and _валиден(A):return{_H:_A,B:_A,_I:_A,_O:'Токен HF валиден.',_R:A}
	return{_H:_A,B:bool(A),_I:_F,_O:'Требуется токен HuggingFace.','подсказка':'https://huggingface.co/settings/tokens'}
def _fetch_card(repo_id,token=''):
	try:
		A=requests.get(f"{_WEB}/{repo_id}/raw/main/README.md",headers=_заголовки(token),timeout=15)
		if A.ok:return A.text
	except Exception:return''
	return''
def поиск_hf_модели(запрос,глубина=_B):
	E=глубина;D=запрос;M={_J:5,_B:15,_C:30}.get(E,15)
	try:
		H=requests.get(f"{_API}/models",headers=_заголовки(_гт()),params={_S:D,_T:M,_U:_K,_V:-1},timeout=15);H.raise_for_status();F=H.json()
		if not F:return f'No models found for: "{D}"'
		I=[f'HuggingFace Models — "{D}" ({len(F)} results):']
		for(N,A)in enumerate(F,1):
			G=A.get('modelId')or A.get('id')or _W;O=A.get(_K,0);P=A.get(_L,0);J=A.get(_d,'');K=', '.join((A.get(_X)or[])[:5]);C=[]
			if A.get(_G):C.append(_e)
			if A.get(_N):C.append('Gated')
			Q=f" [{" ".join(C)}]"if C else'';B=f"{N}. {G}{Q}\n   ▶ {O:,} downloads  ♡ {P} likes"
			if J:B+=f"  • {J}"
			if K and E!=_J:B+=f"\n   Tags: {K}"
			B+=f"\n   • {_WEB}/{G}"
			if E==_C:
				L=_fetch_card(G,_гт())
				if L:B+=f"\n   ➡ {L[:300]}..."
			I.append(B)
		return _D.join(I)
	except Exception as R:return f"HF model search error: {R}"
def поиск_hf_датасеты(запрос,глубина=_B):
	F=глубина;C=запрос;K={_J:5,_B:15,_C:30}.get(F,15)
	try:
		G=requests.get(f"{_API}/datasets",headers=_заголовки(_гт()),params={_S:C,_T:K,_U:_K,_V:-1},timeout=15);G.raise_for_status();D=G.json()
		if not D:return f'No datasets found for: "{C}"'
		H=[f'HuggingFace Datasets — "{C}" ({len(D)} results):']
		for(L,A)in enumerate(D,1):
			I=A.get('id')or _W;M=A.get(_K,0);N=A.get(_L,0);J=', '.join((A.get(_X)or[])[:5]);B=[]
			if A.get(_G):B.append(_e)
			if A.get(_N):B.append('Gated')
			O=f" [{" ".join(B)}]"if B else'';E=f"{L}. {I}{O}\n   ▶ {M:,} downloads  ♡ {N} likes"
			if J and F!=_J:E+=f"\n   Tags: {J}"
			E+=f"\n   ➡ {_WEB}/datasets/{I}";H.append(E)
		return _D.join(H)
	except Exception as P:return f"HF dataset search error: {P}"
def поиск_hf_спейсы(запрос,глубина=_B):
	B=запрос;G={_J:5,_B:15,_C:30}.get(глубина,15)
	try:
		D=requests.get(f"{_API}/spaces",headers=_заголовки(_гт()),params={_S:B,_T:G,_U:_L,_V:-1},timeout=15);D.raise_for_status();C=D.json()
		if not C:return f'No spaces found for: "{B}"'
		E=[f'HuggingFace Spaces — "{B}" ({len(C)} results):']
		for(H,A)in enumerate(C,1):F=A.get('id')or _W;I=A.get(_L,0);J=A.get('sdk','');K=' [Private]'if A.get(_G)else'';E.append(f"{H}. {F}{K}\n   ♡ {I} likes  SDK: {J}\n   ➡ {_WEB}/spaces/{F}")
		return _D.join(E)
	except Exception as L:return f"HF spaces search error: {L}"
def гр_hf(мид,вид=_E,глубина=_B):
	O='siblings';I='N/A';G=глубина;D=вид;A=мид;E=_токен_если_нужно(D,A)
	if not E.get(_I)and E.get(_H):return f'"{A}" не найден или приватный. {E.get(_O,"")}'
	F=E.get(_R,'');J={_E:f"{_API}/models/{A}",_M:f"{_API}/datasets/{A}",_Q:f"{_API}/spaces/{A}"}.get(D,f"{_API}/models/{A}")
	try:
		H=requests.get(J,headers=_заголовки(F),timeout=15)
		if H.status_code==404 and not F:return f'"{A}" не найден или приватный. Требуется токен HF.'
		H.raise_for_status();C=H.json();B=[f"HuggingFace {D.title()}: {A}",f"Author:    {C.get("author",I)}",f"Downloads: ▶ {C.get(_K,0):,}",f"Likes:     ♡ {C.get(_L,0)}"]
		if D==_E:B.append(f"Pipeline:  {C.get(_d,I)}");B.append(f"Library:   {C.get("library_name",I)}")
		if C.get(_N):B.append('⚠️  GATED — токен требуется')
		if C.get(_G):B.append('ⓘ  PRIVATE')
		K=', '.join((C.get(_X)or[])[:10])
		if K:B.append(f"Tags:      {K}")
		B.append(f"URL:       {_WEB}/{"datasets/"if D==_M else"spaces/"if D==_Q else""}{A}")
		if G in{_B,_C}:
			L=_fetch_card(A,F)
			if L:B.append(f"\n--- Model Card (excerpt) ---\n{L[:3000 if G==_C else 1000]}")
		if G==_C and D==_E:
			M=requests.get(J,headers=_заголовки(F),timeout=10,params={'expand[]':O})
			if M.ok:
				N=M.json().get(O,[])
				if N:
					B.append('\n--- Repository Files ---')
					for P in N[:30]:B.append(f"  ⎙ {P.get("rfilename","")}")
		return _D.join(B)
	except Exception as Q:return f"ⓘ – HF Resource Error: {Q}"
def гф_hf(мид,файл,вид=_E):
	B=файл;A=мид;D=_токен_если_нужно(вид,A)
	if not D.get(_I)and D.get(_H):return f'Файл "{B}" в "{A}" требует токен.'
	E=D.get(_R,'')
	if вид==_M:F=f"{_WEB}/datasets/{A}/resolve/main/{B}"
	else:F=f"{_WEB}/{A}/resolve/main/{B}"
	try:
		C=requests.get(F,headers=_заголовки(E),timeout=20)
		if C.status_code==401 and not E:return f'Файл "{B}" в "{A}" требует токен HF.'
		C.raise_for_status()
		try:return C.text[:10000]
		except Exception:return f"[Binary file — {len(C.content)} bytes]"
	except Exception as G:return f"ⓘ – HF File Error: {G}"

if __name__=='__main__':
	import sys,json
	args=sys.argv[1:]
	if not args:
		print("Usage: python huggingface.py <action> <query-or-id> [depth] [extra]")
		sys.exit(1)

	action=args[0]
	depth='medium'

	if args and args[-1] in ('fast','medium','deep'):
		depth=args.pop()

	try:
		if action in ('search-models','models'):
			print(поиск_hf_модели(' '.join(args[1:]),depth))

		elif action in ('search-datasets','datasets'):
			print(поиск_hf_датасеты(' '.join(args[1:]),depth))

		elif action in ('search-spaces','spaces'):
			print(поиск_hf_спейсы(' '.join(args[1:]),depth))

		elif action in ('info','model-info'):
			print(гр_hf(args[1],_E,depth))

		elif action=='file':
			print(гф_hf(args[1],args[2],_E))

		else:
			print(f"Unknown action: {action}")

	except Exception as e:
		print(f"Error: {e}")