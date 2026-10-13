from __future__ import annotations

# كسخت المكتبات حجي


_H=True
_G='struct'
_F='pathspec'
_E='chardet'
_D='urllib3'
_C='requests'
_B=False
_A=_H
import ast,importlib,importlib.util,os,re,shutil,subprocess,sys
from pathlib import Path
Px={_C:_C,_D:_D,'bs4':'beautifulsoup4',_E:_E,_F:_F,'PIL':'Pillow','websocket':'websocket-client','cryptography':'cryptography','psutil':'psutil'}
Sz={'__future__','abc','ast','asyncio','base64','bisect','builtins','collections','colorsys','concurrent','contextlib','copy','csv','dataclasses','datetime','decimal','difflib','dis','email','encodings','enum','errno','fnmatch','fractions','functools','gc','getopt','getpass','glob','gzip','hashlib','heapq','hmac','html','http','importlib','inspect','io','itertools','json','keyword','linecache','locale','logging','lzma','math','mimetypes','multiprocessing','numbers','operator','os','pathlib','pickle','platform','pprint','queue','random','re','resource','select','shelve','shlex','shutil','signal','site','socket','sqlite3','ssl','stat','statistics','string',_G,'subprocess','sys','tarfile','tempfile','textwrap','threading','time','timeit','token','tokenize','trace','traceback','types','typing','unicodedata','unittest','urllib','uuid','warnings','weakref','xml','zipfile','zipimport','zlib','zoneinfo','secrets','sre_compile','sre_constants','sre_parse','codecs','atexit','ntpath','posixpath','array',_G,'hmac','io','_thread'}
импорт=re.compile('\\bimport\\s+([a-zA-Z_][a-zA-Z0-9_]*)')
от=re.compile('\\bfrom\\s+([a-zA-Z_][a-zA-Z0-9_]*)')
G='\x1b[38;2;78;186;101m'
Y='\x1b[38;2;255;193;7m'
R='\x1b[38;2;215;119;87m'
B='\x1b[38;2;177;185;249m'
O='\x1b[0m'
DIM='\x1b[2m'
def ти(path):
	try:
		C=ast.parse(path.read_text(encoding='utf-8',errors='replace'))
	except Exception:return set()
	A=set()
	for B in ast.walk(C):
		if isinstance(B,ast.Import):
			A.update(D.name.split('.')[0] for D in B.names)
		elif isinstance(B,ast.ImportFrom) and B.module and not B.level:
			A.add(B.module.split('.')[0])
	return A
def ит(root):
	B=set()
	for C in root.rglob('*.py'):
		try:A=C.relative_to(root).parts
		except ValueError:A=()
		if 'api' in A[:-1]:continue
		if any(A.startswith('__pycache__')for A in A):continue
		if any(A.startswith('.')for A in A):continue
		B|=ти(C)
	return B
def яв(raw_imports):
	B={}
	for A in raw_imports:
		if A in Sz:continue
		if A in Px:C=Px[A];B[A]=C
	return B
def нт(import_name):
	try:return importlib.util.find_spec(import_name)is not None
	except(ModuleNotFoundError,ValueError):return _B
install_errors={}
def зх(pip_name):
	install_errors.pop(pip_name,None)
	termux='com.termux' in sys.executable or 'com.termux' in os.environ.get('PREFIX','')
	native={'cryptography':'python-cryptography','psutil':'python-psutil','Pillow':'python-pillow'}
	package=native.get(pip_name) if termux else None
	if package:
		pkg=shutil.which('pkg')
		if not pkg:
			install_errors[pip_name]='Termux package manager (pkg) was not found.'
			return _B
		commands=[[pkg,'install','-y',package]]
	else:commands=[[sys.executable,'-m','pip','install','--disable-pip-version-check',pip_name]]
	try:
		result=subprocess.run(commands[0],capture_output=_A,text=_A,timeout=600)
		if package and result.returncode:
			update=subprocess.run([pkg,'update','-y'],capture_output=_A,text=_A,timeout=600)
			if update.returncode==0:result=subprocess.run(commands[0],capture_output=_A,text=_A,timeout=600)
		if result.returncode:
			install_errors[pip_name]=(result.stderr or result.stdout or 'Installer exited with an error.').strip()[-3000:]
			return _B
		importlib.invalidate_caches()
		return _H
	except subprocess.TimeoutExpired:
		install_errors[pip_name]='Installation timed out after 600 seconds.'
		return _B
	except Exception as error:
		install_errors[pip_name]=str(error)
		return _B
frames='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
def проверка(root=None):
	J='com.termux';C=root
	if C is None:C=Path(__file__).resolve().parent
	C=Path(C).resolve();D=C.parts
	if J in D:Q=D.index(J);K=f"com.termux – /{"/".join(D[Q+3:])}"
	else:K=f"{D[-2]} – /{"/".join(D[-2:])}"
	print(f"{B}[⌘]{O} Workspace: {DIM}{K}{O}",flush=_H);S=ит(C);L=яв(S)
	def F():import os,time;time.sleep(2);os.system('clear')
	if not L:print(f"{G}[✓]{O} No dependencies.",flush=_H);F();return
	E=[];M=[]
	for(H,A)in L.items():
		if нт(H):M.append(A)
		else:E.append((H,A))
	for T in M:print(f"  {G}√{O} {T}",flush=_H)
	if not E:print(f"{G}[✔]{O} Dependencies OK.",flush=_H);F();return
	print(f"{Y}[!]{O} Missing: {", ".join(A for(B,A)in E)}",flush=_H);print(f"{B}[⚙]{O} Setup...\n",flush=_H);I=[];import threading as U,itertools as V,time
	for(H,A)in E:
		N=_B
		def W():
			for B in V.cycle(frames):
				if N:break
				print(f"\r  {Y}{B}{O} {A} ",end='',flush=_H);time.sleep(.1)
		P=U.Thread(target=W);P.start();X=зх(A);N=_A;P.join();print('\r',end='',flush=_H)
		if X and not нт(H):X=_B;install_errors[A]='Installer completed, but the module is unavailable to this Python interpreter.'
		if X:print(f"  {G}✓{O} {A}",flush=_H)
		else:
			I.append(A)
			print(f"  {R}✘{O} {A}: {install_errors.get(A,'Installation failed.')}",flush=_H)
	if I:print(f"\n{R}[✘]{O} Install failed: {", ".join(I)}",flush=_H);raise SystemExit(1)
	print(f"\n{G}[✔]{O} Dependencies ready.",flush=_H);F()