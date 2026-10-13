from __future__ import annotations
_a='utils.py'
_Z='__init__.py'
_Y='__pycache__'
_X='textish'
_W='suffix'
_V='binary'
_U='name'
_T='tool-file'
_S='image/'
_R='.py'
_Q='interpreter.'
_P=False
_O='hints'
_N='replace'
_M='utf-8'
_L='preview'
_K='functions'
_J=True
_I='\\'
_H=None
_G='run_command'
_F='doc'
_E='module'
_D='loaded'
_C='kind'
_B='/'
_A='path'
import ast,importlib.util,mimetypes,sys
from pathlib import Path
_dir=Path(__file__).parent
_м={}
_мета={}
_файлы={}
_ошибки_загрузки={}
_workspace=None
_SKIP=['__init__']
_EAGER=['filesystem','utils']
_HIDDEN_DIRS={'ЯТИ'}
_CODE_SUFFIXES={_R,'.pyi','.txt','.md','.rst','.json','.yaml','.yml','.toml','.ini','.cfg','.conf','.sh','.bash','.zsh','.env','.sql','.csv','.tsv','.xml','.html','.htm','.css','.js','.ts','.jsx','.tsx','.php','.rb','.go','.rs','.java','.c','.h','.cpp','.hpp','.cs','.kt','.swift','.dart','.lua','.pyw','.ps1','.mk','.make','.cmake','.gradle'}
_IMAGE_SUFFIXES={'.png','.jpg','.jpeg','.webp','.gif','.bmp','.ico','.tif','.tiff'}
def _is_codeish(path):A=path.suffix.lower();B,C=mimetypes.guess_type(str(path));return A in _CODE_SUFFIXES or(B or'').startswith('text/')
def _shebang_interpreter(path):
	"Extract interpreter from a #! line, e.g. '#!/usr/bin/env python3' -> 'python3'."
	try:
		with path.open('rb')as E:C=E.readline(200).decode(_M,_N).strip()
	except Exception:return''
	if not C.startswith('#!'):return''
	A=C[2:].strip().split()
	if not A:return''
	B=A[0].split(_B)[-1]
	if B=='env':D=[A for A in A[1:]if not A.startswith('-')];B=D[0].split(_B)[-1]if D else''
	return B
def _run_command(path):
	A=path;B=A.suffix.lower()
	if B==_R:return f"python {A}"
	if B in{'.sh','.bash','.zsh'}:return f"bash {A}"
	if B=='.js':return f"node {A}"
	if B=='.ts':return f"node {A}  # or tsx/ts-node"
	if B=='.php':return f'php {A}  # argv-style: php {A} "VALUE". If it reads $_GET/$_POST, do NOT append "?k=v"; inject instead: php -r \'$_GET["q"]="VALUE"; include "{A}";\' (or php -S 127.0.0.1:PORT -t {A.parent} + curl localhost)'
	if B=='.rb':return f"ruby {A}"
	if B=='.pl':return f"perl {A}"
	if B=='.lua':return f"lua {A}"
	if B=='.ps1':return f"pwsh {A}"
	if B=='.dart':return f"dart {A}"
	if B=='.groovy':return f"groovy {A}"
	if B=='.go':return f"go run {A}"
	if B=='.rs':return f"cargo run --manifest-path {A.parent/"Cargo.toml"}"
	if B=='.java':return f"javac {A} && java {A.stem}"
	if B=='.pyw':return f"pythonw {A}"
	if B=='.sql':return'Use your database client / psql / mysql depending on the project'
	if B in _IMAGE_SUFFIXES:return'Open as image file; not executable'
	C=_shebang_interpreter(A)if A.is_file()else''
	if C:return f"{C} {A}"
	if A.is_file()and A.exists():return'Inspect source first, then run with the appropriate interpreter'
	return'No safe run command inferred'
def _source_preview(path,limit_lines=8,limit_chars=2200):
	D=limit_chars;B=path
	try:
		E,I=mimetypes.guess_type(str(B));C=B.suffix.lower();G=C in _CODE_SUFFIXES or(E or'').startswith('text/')
		if not G:
			if(E or'').startswith(_S)or C in _IMAGE_SUFFIXES:return f"[{C or _V} asset]"
			return''
		F=B.read_text(encoding=_M,errors=_N)
	except Exception:return''
	H=F.splitlines();A='\n'.join(H[:limit_lines]).strip()
	if len(A)>D:A=A[:D]
	if len(F)>len(A):A+='\n… [truncated]'
	return A
def _extract_meta(path):
	B=path;A={_F:'',_K:[],_O:[],_A:str(B),_C:_T,_D:_P,_G:_run_command(B),_W:B.suffix.lower()}
	try:E=B.read_text(encoding=_M,errors=_N)
	except Exception:return A
	F=[]
	for I in E.splitlines():
		D=I.strip()
		if D.startswith('#'):F.append(D[1:].strip())
		elif D:break
	A[_O]=F
	try:G=ast.parse(E)
	except SyntaxError:return A
	except Exception:return A
	H=ast.get_docstring(G)
	if H:A[_F]=H
	for C in G.body:
		if isinstance(C,(ast.FunctionDef,ast.AsyncFunctionDef))and not C.name.startswith('_'):A[_K].append({_U:C.name,_F:ast.get_docstring(C)or'','signature':C.name+'('+ast.unparse(C.args)+')'})
	A[_L]=_source_preview(B);return A
def _file_meta(path):
	A=path
	try:C=A.stat()
	except Exception:C=_H
	D=A.suffix.lower();E,G=mimetypes.guess_type(str(A));F=_is_codeish(A);B=(E or'').startswith(_S)or D in _IMAGE_SUFFIXES;return{_U:A.name,_A:str(A),'relpath':str(A.relative_to(_dir))if A.is_relative_to(_dir)else A.name,_W:D,'size':getattr(C,'st_size',_H),'mtime':getattr(C,'st_mtime',_H),'mime':E or'',_X:F and not B,'imageish':B,_C:'text'if F and not B else'image'if B else _V,_L:_source_preview(A),_G:_run_command(A)}
def _index_files():
	for A in sorted(_dir.rglob('*')):
		if not A.is_file():continue
		if _Y in A.parts:continue
		if A.name.startswith('.'):continue
		if A.name in[_Z,_a]:continue
		B=A.relative_to(_dir)
		if B.parts and B.parts[0]in _HIDDEN_DIRS:continue
		if not _is_codeish(A)and not(mimetypes.guess_type(str(A))[0]or'').startswith(_S):continue
		_файлы[str(B)]=_file_meta(A)
def _load_all():
	I='display_name';_index_files()
	for A in sorted(_dir.rglob('*.py')):
		if _Y in A.parts:continue
		E=A.stem;J=str(A.relative_to(_dir).with_suffix('')).replace(_I,_B);G=J in _EAGER or E in _EAGER;H=A.relative_to(_dir).parts;K=len(H)>1 and H[0]in _HIDDEN_DIRS
		if E.startswith('_')or E in _SKIP:continue
		if K and not G:continue
		try:
			C=A.stem
			try:C=A.name[:-3].encode('raw_unicode_escape').decode('unicode_escape')
			except Exception:pass
			if G:
				D=importlib.util.spec_from_file_location(_Q+C,str(A))
				if D and D.loader:F=importlib.util.module_from_spec(D);sys.modules[_Q+C]=F;D.loader.exec_module(F);_м[C]=F;B=_extract_meta(A);B[_D]=_J;B[_C]=_E;B[I]=C;_мета[C]=B;continue
			B=_extract_meta(A);B[_D]=_P;B[_C]=_T;B[I]=C;_мета[C]=B
		except Exception:continue
def _set_workspace(path):
	global _workspace
	_workspace=Path(path).resolve()
	for name,module in _м.items():
		if name in('filesystem','media','download-web-files'):module.ROOT=_workspace
		elif name=='browser-agent':module._ROOT=_workspace
def _load_module(display_name):
	A=display_name
	if A in _м:return _м[A]
	B=_мета.get(A)
	if not B:return
	E=B.get(_A,'')
	if not E:return
	try:
		C=importlib.util.spec_from_file_location(_Q+A,E)
		if not C or not C.loader:return
		D=importlib.util.module_from_spec(C);sys.modules[_Q+A]=D;C.loader.exec_module(D);_м[A]=D;B[_D]=_J;B[_C]=_E;
		if _workspace is not None:_set_workspace(_workspace)
		return D
	except (Exception,SystemExit) as error:
		_ошибки_загрузки[A]=f"{type(error).__name__}: {error}"
		return
_load_all()
def список_файлов(include_hidden=_P):
	A=[]
	for(B,C)in sorted(_файлы.items()):
		if not include_hidden and Path(B).name.startswith('.'):continue
		A.append(C.copy())
	return A
def список_инструментов():
	S='direct';R='small_text_only';Q='exec_mode';P='edit_policy';O='trusted_builtin';N='hint';E=' | ';F=[];J=set()
	for(C,A)in sorted(_мета.items()):B=A.get(_A,'');F.append({_E:C,_A:B,_C:A.get(_C,_E),_D:A.get(_D,_P),_K:[A[_U]for A in A.get(_K,[])],'signatures':[entry.get('signature',entry[_U]) for entry in A.get(_K,[])],_F:A.get(_F)or E.join(A.get(_O,[])),N:E.join(A.get(_O,[])),_L:A.get(_L,''),_G:A.get(_G,''),O:_J,P:R,Q:S});J.add(Path(B).name if B else C)
	for(B,A)in sorted(_файлы.items()):
		C=Path(B).stem
		if Path(B).name in[_Z,_a]:continue
		if not A.get(_X):continue
		if Path(B).suffix.lower()==_R and C in _мета:continue
		if B in J:continue
		try:D=Path(A.get(_A,_dir/B)).read_text(encoding=_M,errors=_N)
		except Exception:D=''
		K='';G=[];L=[]
		for T in D.splitlines():
			H=T.strip()
			if H.startswith('#'):G.append(H[1:].strip())
			elif H:break
		if D:
			try:
				M=ast.parse(D);K=ast.get_docstring(M)or''
				for I in ast.walk(M):
					if isinstance(I,(ast.FunctionDef,ast.AsyncFunctionDef))and not I.name.startswith('_'):L.append(I.name)
			except Exception:pass
		F.append({_E:C,_A:B,_C:A.get(_C,_T),_D:_P,_K:L,_F:K or E.join(G),N:E.join(G),_L:_source_preview(Path(A.get(_A,_dir/B))if A.get(_A)else _dir/B),_G:A.get(_G,''),O:_J,P:R,Q:S})
	return F
def вызвать(модуль,функция,*E,**F):
	B=функция;A=модуль;D=_load_module(A)
	if D is _H:return f"Module load failed: {A}: {_ошибки_загрузки[A]}"if A in _ошибки_загрузки else f"Module not found: {A}"
	C=getattr(D,B,_H)
	if C is _H or not callable(C):return f"Function not found: {A}.{B}"
	try:
		import inspect
		parameters=inspect.signature(C).parameters
		if A=='filesystem' and 'путь' in parameters and 'path' in F and 'path' not in parameters and 'путь' not in F:F['путь']=F.pop('path')
		import io,contextlib
		output=io.StringIO()
		with contextlib.redirect_stdout(output):result=C(*E,**F)
		printed=output.getvalue()
		if printed:print(printed,end='')
		return printed if result is _H and printed else result
	except TypeError as G:
		import inspect
		return f"Error calling interpreter.{A}.{B}: {G}. Expected: {B}{inspect.signature(C)}"
	except Exception as G:return f"Error calling interpreter.{A}.{B}: {G}"
try:from.режим import пуск
except Exception:
	def пуск(*A,**B):0
def найти_инструмент(имя):
	A=str(имя or'').strip().lower().replace(_I,_B).replace(_I,_B)
	if not A:return
	F=[]
	for(E,B)in _мета.items():
		F.append((E.lower(),B));G=str(B.get(_A,'')).lower().replace(_I,_B);C=str(B.get(_A,'')).split(_B)[-1].lower();D=Path(B.get(_A,'')).stem.lower()
		if A in{E.lower(),C,D}or A in G or A in C or A in D:return B.copy()|{_E:E}
	for(C,B)in _файлы.items():
		H=C.lower().replace(_I,_B);D=Path(C).stem.lower()
		if A in H or A in D or A==Path(C).name.lower():return B.copy()|{_E:D}
def инструмент_по_пути(путь):
	B=Path(str(путь or'').replace(_I,_B));A=str(B).lstrip('./')
	if A in _файлы:return _файлы[A].copy()
	return найти_инструмент(B.name or A)
def каталог_инструментов(include_non_loaded=_J):'Return discovered tool files and loaded modules.';A=список_инструментов();return A if include_non_loaded else[A for A in A if A.get(_D)]
__all__=['_м','_мета','_файлы','список_файлов','список_инструментов','каталог_инструментов','найти_инструмент','инструмент_по_пути','вызвать','пуск']

# данный проект был разработан: T.me/sii_3
