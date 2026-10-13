from __future__ import annotations

# ВАЖНО: не удалите этот инструмент он необходим для корректнои работы в вашеи среде ^_^ [ данныи текст адресован пользователю не программе ]

# Usage (via TOOL: run_file, or directly):
# python github.py <action> <repository-or-query> [depth] [extra]
# "python" – "python3 -->> APPLIES TO THE SYSTEM
# GitHub toolkit for searching repositories, inspecting repositories, reading files,
# viewing issues, and accessing GitHub repository information.
#
# Supported actions:
# search       – Search GitHub repositories by name, topic, or keywords.
# info         – Get detailed repository information.
# file         – Read a specific file from a repository.
# tree         – Get repository file structure.
# issues       – Get repository issues.
#
# Depth levels:
# fast     – Quick results with minimal information.
# medium   – More metadata, README excerpts, and details (default).
# deep     – Extended information including file tree and additional repository data.
#
# Token:
# Public repositories work without a token.
# Private repositories or restricted resources require GH_TOKEN or GITHUB_TOKEN.
#
# Use this tool when you need GitHub repositories, source files, project structure,
# stars, forks, languages, README content, issues, or repository analysis.


_Z='language'
_Y='forks_count'
_X='stargazers_count'
_W='description'
_V='full_name'
_U='per_page'
_T='application/vnd.github+json'
_S='Accept'
_R='Authorization'
_Q='GH_TOKEN='
_P='GITHUB_TOKEN='
_O='.darkps'
_N='replace'
_M='default_branch'
_L='fast'
_K='сообщ'
_J='валид'
_I='нужен'
_H='utf-8'
_G='deep'
_F=False
_E='N/A'
_D='\n'
_C='medium'
_B='main'
_A=True
import base64,os,urllib.parse
from pathlib import Path
import requests
_API='https://api.github.com'
_WEB='https://github.com'
def _гт():
	B=os.getenv('GITHUB_TOKEN','')or os.getenv('GH_TOKEN','')
	if B:return B
	C=Path.home()/_O/'.env'
	if C.exists():
		for A in C.read_text(encoding=_H,errors=_N).splitlines():
			if A.startswith(_P)or A.startswith(_Q):return A.split('=',1)[1].strip().strip('"').strip("'")
	return''
def сгт(token):
	D=token;E=Path.home()/_O;E.mkdir(parents=_A,exist_ok=_A);B=E/'.env';G=B.read_text(encoding=_H,errors=_N).splitlines()if B.exists()else[];A=[];F=_F
	for C in G:
		if C.startswith(_P)or C.startswith(_Q):A.append(f"GITHUB_TOKEN={D}");F=_A
		else:A.append(C)
	if not F:A.append(f"GITHUB_TOKEN={D}")
	B.write_text(_D.join(A)+_D,encoding=_H)
def пгт(token):сгт(token)
def _валиден(token):
	try:A=requests.get(f"{_API}/user",headers={_R:f"token {token}",_S:_T},timeout=10);return A.status_code==200
	except Exception:return _F
def _заголовки(token=''):
	A=token;B={_S:_T,'User-Agent':'DarkPs-Agent/1.0'}
	if A:B[_R]=f"token {A}"
	return B
def _требует_токен(repo_id):
	try:A=requests.get(f"{_API}/repos/{repo_id}",headers=_заголовки(),timeout=10);return A.status_code in{401,403,404}
	except Exception:return _F
def _получить_токен_если_нужно(repo_id='',действие='read'):
	C=repo_id;B='есть';A=_гт()
	if C and not _требует_токен(C):return{_I:_F,B:bool(A),_J:_A,_K:'Публичный ресурс, токен не нужен.'}
	if A and _валиден(A):return{_I:_A,B:_A,_J:_A,_K:'Токен GitHub валиден.','токен':A}
	return{_I:_A,B:bool(A),_J:_F,_K:'Требуется токен GitHub.','подсказка':'https://github.com/settings/tokens','действие':действие}
def _читать_файл_репо(repo_id,path,branch=_B,token=''):
	F='download_url';E='content';B=token
	if not path:return''
	G=f"{_API}/repos/{repo_id}/contents/{urllib.parse.quote(path)}"
	try:
		C=requests.get(G,headers=_заголовки(B),params={'ref':branch},timeout=15)
		if not C.ok:return''
		A=C.json()
		if isinstance(A,dict)and A.get('encoding')=='base64'and A.get(E):H=base64.b64decode(A[E]);return H.decode(_H,errors=_N)
		if isinstance(A,dict)and A.get(F):
			D=requests.get(A[F],headers=_заголовки(B),timeout=15)
			if D.ok:return D.text
	except Exception:return''
	return''
def _листинг_репо(repo_id,path='',branch=_B,token=''):
	C=token;B=branch;A=repo_id
	try:
		if path:
			D=_читать_файл_репо(A,path,B,C)
			if D:return D[:3000]
			return''
		E=requests.get(f"{_API}/repos/{A}/git/trees/{B}",headers=_заголовки(C),params={'recursive':1},timeout=20)
		if not E.ok:return''
		J=E.json().get('tree',[]);F=[]
		for G in J[:200]:
			H=G.get('type','');I=G.get('path','')
			if H and I:F.append(f"{H}: {I}")
		return _D.join(F)
	except Exception:return''
def гп(запрос,глубина=_C):
	E=глубина;B=запрос;J={_L:5,_C:15,_G:30}.get(E,15)
	try:
		F=requests.get(f"{_API}/search/repositories",headers=_заголовки(_гт()),params={'q':B,_U:J,'sort':'stars','order':'desc'},timeout=15);F.raise_for_status();C=F.json().get('items',[])
		if not C:return f'No repositories found: "{B}"'
		G=[f'GitHub Repositories — "{B}" ({len(C)} results):']
		for(K,A)in enumerate(C,1):
			D=A.get(_V,'unknown');L=A.get(_W)or'No description';M=A.get(_X,0);N=A.get(_Y,0);O=A.get(_Z)or _E;H=f"{K}. {D}\n   ⭐ {M} | 🍴 {N} | Lang: {O}\n   {L}\n   {_WEB}/{D}"
			if E==_G:
				I=_листинг_репо(D,'',A.get(_M,_B),_гт())
				if I:H+=f"\n   Files:\n{I[:2500]}"
			G.append(H)
		return'\n\n'.join(G)
	except Exception as P:return f"GitHub search error: {P}"
def гр(рп,глубина=_C):
	G=глубина;B=рп;C=_получить_токен_если_нужно(B)
	if not C.get(_J)and C.get(_I):return f'Репозиторий "{B}" не найден или приватный. {C.get(_K,"")}'
	D=C.get('токен','')
	try:
		E=requests.get(f"{_API}/repos/{B}",headers=_заголовки(D),timeout=15)
		if E.status_code==404 and not D:return f'Репозиторий "{B}" не найден или приватный. Требуется токен.'
		E.raise_for_status();A=E.json();F=[f"Repo:        {A.get(_V,B)}",f"Description: {A.get(_W,_E)}",f"Stars: ⭐ {A.get(_X,0)}  Forks: 🍴 {A.get(_Y,0)}  Issues: ⚠ {A.get("open_issues_count",0)}",f"Language:    {A.get(_Z,_E)}",f"Branch:      {A.get(_M,_B)}",f"License:     {(A.get("license")or{}).get("name",_E)}",f"Created:     {str(A.get("created_at",_E))[:10]}",f"Updated:     {str(A.get("updated_at",_E))[:10]}",f"URL:         {A.get("html_url",f"{_WEB}/{B}")}",f"Clone:       {A.get("clone_url","")}"]
		if G in{_C,_G}:
			H=_читать_файл_репо(B,'README.md',A.get(_M,_B),D)
			if H:F.append(f"\n--- README (excerpt) ---\n{H[:1500]}")
		if G==_G:
			I=_листинг_репо(B,'',A.get(_M,_B),D)
			if I:F.append(f"\n--- File Tree ---\n{I}")
		return _D.join(F)
	except Exception as J:return f"GitHub repo error: {J}"
def гс(рп,путь='',ветка=_B,глубина=_C):
	E=глубина;D=ветка;A=путь;F=_гт()
	if A:
		B=_читать_файл_репо(рп,A,D,F)
		if not B:return f'File "{A}" not found in "{рп}".'
		return B[:12000]if E!=_L else B[:4000]
	C=_листинг_репо(рп,'',D,F)
	if C:return C if E!=_L else _D.join(C.splitlines()[:80])
	return f'No tree available for "{рп}".'
def ги(рп,глубина=_C,state='open'):
	E=_гт()
	try:
		C=requests.get(f"{_API}/repos/{рп}/issues",headers=_заголовки(E),params={'state':state,_U:{_L:5,_C:15,_G:30}.get(глубина,15)},timeout=15)
		if not C.ok:return f'Issues unavailable for "{рп}".'
		A=C.json()
		if not A:return f'No issues found for "{рп}".'
		D=[f'GitHub Issues — "{рп}" ({len(A)} results):']
		for B in A[:30]:F=B.get('number','?');G=B.get('title','');H=(B.get('user')or{}).get('login','?');D.append(f"  #{F} [{H}] {G}")
		return _D.join(D)
	except Exception as I:return f"Issues error: {I}"
	
if __name__=='__main__':
	import sys
	args=sys.argv[1:]

	if not args:
		print("Usage: python github.py <action> <repository-or-query> [depth] [extra]")
		sys.exit(1)

	action=args[0]
	depth='medium'

	if args and args[-1] in ('fast','medium','deep'):
		depth=args.pop()

	try:
		if action in ('search','repos'):
			print(гп(' '.join(args[1:]),depth))

		elif action in ('info','repo'):
			print(гр(args[1],depth))

		elif action=='file':
			print(гс(args[1],args[2] if len(args)>2 else '',глубина=depth))

		elif action=='tree':
			print(гс(args[1],'',глубина=depth))

		elif action=='issues':
			print(ги(args[1],depth))

		else:
			print(f"Unknown action {action}")

	except Exception as e:
		print(f"{e}")