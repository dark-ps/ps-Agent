# ВАЖНО: не удалите этот инструмент он необходим для корректнои работы в вашеи среде ^_^

from __future__ import annotations
_G='строка'
_F='кон'
_E='нач'
_D='файл'
_C='replace'
_B='ошибка'
_A='utf-8'
import ast,re,textwrap
from pathlib import Path
class пт:
	def __init__(A,к=None):A.к=Path(к)if к else Path.cwd()
	def найти_функцию(H,ф,и):
		G=H.к/ф
		if not G.exists():return{_B:f"➡ Файл не найден - {ф}"}
		A=G.read_text(encoding=_A,errors=_C).splitlines();I=[rf"^(async\s+)?def\s+{re.escape(и)}\s*\(",rf"^class\s+{re.escape(и)}\s*[\(:]"]
		for(D,E)in enumerate(A):
			for J in I:
				if re.match(J,E):
					F=D;K=len(E)-len(E.lstrip());B=D+1
					for C in range(D+1,len(A)):
						L=A[C].strip()
						if not L:B=C+1;continue
						if len(A[C])-len(A[C].lstrip())<=K:break
						B=C+1
					return{_D:ф,'имя':и,_E:F+1,_F:B,'строки':A[F:B],'кол_строк':B-F}
		return{_B:f"Не найдено {и} в {ф}"}
	def заменить_функцию(B,ф,и,тело):
		A=B.найти_функцию(ф,и)
		if _B in A:return A
		C=B.к/ф;D=C.read_text(encoding=_A,errors=_C).splitlines();T=textwrap.dedent(тело).strip('\n');E=D[:A[_E]-1]+T.splitlines()+D[A[_F]:];N='\n'.join(E)+'\n'
		if C.suffix=='.py':
			try:ast.parse(N)
			except SyntaxError as X:return{_B:f'Invalid replacement; file unchanged: {X}'}
		C.write_text(N,encoding=_A);return{'успех':True,_D:ф,'заменено':и,'старые_строки':f"{A[_E]}-{A[_F]}"}
	def найти_переменную(D,ф,п):
		A=D.к/ф
		if not A.exists():return{_B:f"Файл не найден:{ф}"}
		E=A.read_text(encoding=_A,errors=_C);B=[]
		for(F,C)in enumerate(E.splitlines(),1):
			if re.search(rf"\b{re.escape(п)}\b",C):B.append({_G:F,'текст':C.strip()})
		return B
	def grep(A,ш):
		B=[]
		for C in A.к.rglob('*.py'):
			try:E=C.read_text(encoding=_A,errors=_C)
			except Exception:continue
			for(F,D)in enumerate(E.splitlines(),1):
				if re.search(ш,D):B.append({_D:str(C.relative_to(A.к)),_G:F,'текст':D.strip()})
		return B
	def refactor_imports(B,ф):
		A=B.к/ф
		if not A.exists():return{_B:f"Файл не найден:{ф}"}
		C=A.read_text(encoding=_A,errors=_C);return{_D:ф,'импортов':len(re.findall('^\\s*(from\\s+\\S+\\s+import|import\\s+\\S+)',C,re.M))}
	def дерево(A,глубина=3):
		return [str(p.relative_to(A.к)) + ('/' if p.is_dir() else '') for p in sorted(A.к.rglob('*')) if len(p.relative_to(A.к).parts)<=int(глубина)]
	def греп(A,ш,расширение='.py'):
		B=[]
		for C in A.к.rglob('*'+расширение):
			if not C.is_file():continue
			for N,L in enumerate(C.read_text(encoding=_A,errors=_C).splitlines(),1):
				if re.search(ш,L):B.append({_D:str(C.relative_to(A.к)),_G:N,'текст':L.strip()})
		return B
	def рефактор_импортов(A,ф,старый,новый):
		P=A.к/ф
		if not P.is_file():return{_B:f"Файл не найден:{ф}"}
		T=P.read_text(encoding=_A);N=0;L=[]
		for S in T.splitlines(keepends=True):
			if re.match(r'^\s*(from|import)\s+',S):
				S,C=re.subn(r'(?<![\w.])'+re.escape(старый)+r'(?!\w)',lambda m:новый,S);N+=C
			L.append(S)
		P.write_text(''.join(L),encoding=_A);return{'успех':True,'замены':N}
	def пакетное_переименование(A,список):
		P=[]
		for I in список:
			S,D=(I.get('old'),I.get('new')) if isinstance(I,dict) else I
			S=(A.к/S).resolve();D=(A.к/D).resolve()
			if not S.is_relative_to(A.к.resolve()) or not D.is_relative_to(A.к.resolve()) or not S.exists() or D.exists():return{_B:'Invalid source or destination'}
			P.append((S,D))
		if len({D for S,D in P})!=len(P) or len({S for S,D in P})!=len(P):return{_B:'Duplicate paths'}
		for S,D in P:D.parent.mkdir(parents=True,exist_ok=True);S.rename(D)
		return{'успех':True,'переименовано':len(P)}

пт0=пт()