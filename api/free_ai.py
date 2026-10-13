# api/free_ai.py

def free_ai(model,messages):
	H='choices';E='content';D=True;import json,time,requests as I,random as C;J=f"Mozilla/5.0 (Linux; Android {C.randint(8,14)}; {C.choice(["K","SM-G991B","Pixel","Redmi"])}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{C.randint(120,135)}.0.0.0 Mobile Safari/537.36";F=I.Session();F.headers.update({'accept':'*/*','content-type':'application/json','origin':'https://free.ai','user-agent':J});K=F.post('https://api.free.ai/v1/chat/',json={'messages':messages,'model':model,'stream':D,'lang':'ru'},stream=D,timeout=(15,120))
	if K.status_code>=400:
		try:detail=K.json().get('error','')
		except Exception:detail=''
		if detail:raise I.HTTPError(f'Free AI HTTP {K.status_code}: {detail}',response=K)
		K.raise_for_status()
	deadline=time.monotonic()+180
	for A in K.iter_lines(decode_unicode=D,chunk_size=1):
		if time.monotonic()>=deadline:raise TimeoutError("Free AI response timed out")
		if not A:continue
		if A.startswith('data: '):A=A[6:]
		if A=='[DONE]':break
		try:
			B=json.loads(A)
			if E in B:yield B[E]
			elif H in B:
				G=B[H][0]['delta'].get(E)
				if G:yield G
		except Exception:continue

# - By: T.me/sii_3