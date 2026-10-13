from __future__ import annotations
_O='<style[^>]*>.*?</style>'
_N='<script[^>]*>.*?</script>'
_M='<title[^>]*>(.*?)</title>'
_L='medium'
_K='content_type'
_J='status'
_I='keywords'
_H='description'
_G='\n'
_F='title'
_E=' '
_D='links'
_C='images'
_B='text'
_A='url'
import re,time,urllib.parse
from typing import Optional
import requests
_UA_DESKTOP='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
_UA_MOBILE='Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36'
_DEFAULT_HEADERS={'User-Agent':_UA_DESKTOP,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en-US,en;q=0.9,ar;q=0.8','Accept-Encoding':'gzip, deflate, br','Cache-Control':'no-cache','DNT':'1'}
def _получить_страницу(url,таймаут=15,заг=None):
	E='utf-8';B=таймаут;C={**_DEFAULT_HEADERS,**(заг or{})}
	try:
		D=requests.Session();D.max_redirects=10;A=D.get(url,headers=C,timeout=B,allow_redirects=True)
		if A.encoding and A.encoding.lower()not in(E,'utf8'):
			try:return A.content.decode(E,errors='replace')
			except Exception:pass
		return A.text
	except requests.exceptions.SSLError:
		try:A=requests.get(url,headers=C,timeout=B,verify=False);return A.text
		except Exception:return''
	except Exception:return''
def _получить_страницу_с_мета(url,таймаут=20):
	F='html';E=url;A={_A:E,_F:'',_H:'',_I:'',F:'',_B:'',_D:[],_C:[],_J:0,_K:''};G={**_DEFAULT_HEADERS}
	try:
		H=requests.Session();D=H.get(E,headers=G,timeout=таймаут,allow_redirects=True);A[_J]=D.status_code;A[_K]=D.headers.get('content-type','');A[_A]=D.url
		if not D.ok:return A
		C=D.text;A[F]=C;B=re.search(_M,C,re.I|re.S)
		if B:A[_F]=_очистить_текст(B.group(1))
		for I in['<meta[^>]+name=["\\\']description["\\\'][^>]+content=["\\\']([^"\\\']+)["\\\']','<meta[^>]+content=["\\\']([^"\\\']+)["\\\'][^>]+name=["\\\']description["\\\']','<meta[^>]+property=["\\\']og:description["\\\'][^>]+content=["\\\']([^"\\\']+)["\\\']']:
			B=re.search(I,C,re.I)
			if B:A[_H]=B.group(1).strip();break
		B=re.search('<meta[^>]+name=["\\\']keywords["\\\'][^>]+content=["\\\']([^"\\\']+)["\\\']',C,re.I)
		if B:A[_I]=B.group(1).strip()
		A[_B]=_извлечь_весь_текст(C);A[_D]=_извлечь_ссылки(C,E);J=re.findall('<img[^>]+src=["\\\']([^"\\\']+)["\\\']',C,re.I);A[_C]=[_абсолютный_url(A,E)for A in J[:30]]
	except Exception as K:A['error']=str(K)
	return A
def _очистить_текст(т):т=re.sub('<[^>]+>',_E,т);т=re.sub('&nbsp;',_E,т);т=re.sub('&amp;','&',т);т=re.sub('&lt;','<',т);т=re.sub('&gt;','>',т);т=re.sub('&quot;','"',т);т=re.sub('&#\\d+;','',т);т=re.sub('&[a-z]+;','',т);return re.sub('\\s+',_E,т).strip()
def _извлечь_весь_текст(html):A=html;A=re.sub(_N,_E,A,flags=re.S|re.I);A=re.sub(_O,_E,A,flags=re.S|re.I);A=re.sub('<noscript[^>]*>.*?</noscript>',_E,A,flags=re.S|re.I);A=re.sub('<!--.*?-->',_E,A,flags=re.S);A=re.sub('<(br|p|div|h[1-6]|li|tr|section|article)[^>]*>',_G,A,flags=re.I);A=re.sub('</(p|div|section|article)>',_G,A,flags=re.I);B=_очистить_текст(A);B=re.sub('\\n{3,}','\n\n',B);return B.strip()
def _извлечь_описание(html):
	B=html
	if not B:return''
	for G in['<meta[^>]+name=["\\\']description["\\\'][^>]+content=["\\\']([^"\\\']{20,})["\\\']','<meta[^>]+content=["\\\']([^"\\\']{20,})["\\\'][^>]+name=["\\\']description["\\\']','<meta[^>]+property=["\\\']og:description["\\\'][^>]+content=["\\\']([^"\\\']{20,})["\\\']']:
		C=re.search(G,B,re.I)
		if C:return C.group(1).strip()[:300]
	A=re.sub(_N,'',B,flags=re.S|re.I);A=re.sub(_O,'',A,flags=re.S|re.I);H=re.findall('<p[^>]*>(.*?)</p>',A,re.S|re.I)
	for I in H:
		D=_очистить_текст(I)
		if len(D)>60:return D[:300]
	E=re.search('<body[^>]*>(.*?)</body>',A,re.S|re.I)
	if E:
		F=_очистить_текст(E.group(1))
		if F:return F[:300]
	return''
def _извлечь_заголовок(html):
	A=re.search(_M,html,re.I|re.S)
	if A:return _очистить_текст(A.group(1))
	A=re.search('<h1[^>]*>(.*?)</h1>',html,re.I|re.S)
	if A:return _очистить_текст(A.group(1))
	return''
def _извлечь_ссылки(html,базовый_url=''):
	B=[];C=set()
	for D in re.finditer('<a[^>]+href=["\\\']([^"\\\'#][^"\\\']*)["\\\'][^>]*>(.*?)</a>',html,re.I|re.S):
		E=D.group(1).strip();F=_очистить_текст(D.group(2));A=_абсолютный_url(E,базовый_url)
		if A and A not in C and A.startswith('http'):C.add(A);B.append({_A:A,_B:F[:100]})
	return B
def _абсолютный_url(href,базовый):
	B=базовый;A=href
	if not A:return''
	if A.startswith('//'):D=urllib.parse.urlparse(B).scheme or'https';return f"{D}:{A}"
	if A.startswith('http'):return A
	if A.startswith('/'):C=urllib.parse.urlparse(B);return f"{C.scheme}://{C.netloc}{A}"
	try:return urllib.parse.urljoin(B,A)
	except Exception:return A
def глубокий_анализ_сайта(url,глубина=_L):
	I=глубина;H='=';D=url
	if I=='fast':
		E=_получить_страницу(D,таймаут=10)
		if not E:return f"Could not fetch: {D}"
		L=_извлечь_заголовок(E);M=_извлечь_описание(E);J=_извлечь_ссылки(E,D)[:10];B=[f"URL: {D}",f"Title: {L}",f"Description: {M}",f"Top links ({len(J)}):"]
		for C in J:B.append(f"  • {C[_B]} → {C[_A]}")
		return _G.join(B)
	elif I==_L:
		A=_получить_страницу_с_мета(D,таймаут=20);B=[f"URL: {A[_A]}",f"Status: {A[_J]}",f"Title: {A[_F]}",f"Description: {A[_H]}",f"Keywords: {A[_I]}",f"Content-Type: {A[_K]}",f"\n--- Page Content ---\n{A[_B][:5000]}",f"\n--- Links found ({len(A[_D])}) ---"]
		for C in A[_D][:20]:B.append(f"  • {C[_B][:60]} → {C[_A]}")
		if A[_C]:
			B.append(f"\n--- Images ({len(A[_C])}) ---")
			for F in A[_C][:10]:B.append(f"  ⛶ {F}")
		return _G.join(B)
	else:
		A=_получить_страницу_с_мета(D,таймаут=25);B=[f"═══ DEEP ANALYSIS: {D} ═══",f"Status: {A[_J]}  Content-Type: {A[_K]}",f"Title: {A[_F]}",f"Description: {A[_H]}",f"Keywords: {A[_I]}",f"\n{H*50}",f"FULL PAGE CONTENT:",A[_B][:8000],f"\n{H*50}",f"ALL LINKS ({len(A[_D])}):"]
		for C in A[_D][:40]:B.append(f"  • [{C[_B][:50]}] → {C[_A]}")
		if A[_C]:
			B.append(f"\nIMAGES ({len(A[_C])}):")
			for F in A[_C][:20]:B.append(f"  ⛶ {F}")
		N=urllib.parse.urlparse(D).netloc;G=[A for A in A[_D]if urllib.parse.urlparse(A[_A]).netloc==N and A[_A]!=D][:5]
		if G:
			B.append(f"\n{H*50}");B.append(f"CRAWLING {len(G)} SUB-PAGES:")
			for C in G:B.append(f"\n--- Sub-page: {C[_A]} ---");K=_получить_страницу_с_мета(C[_A],таймаут=15);B.append(f"Title: {K[_F]}");B.append(f"Content: {K[_B][:2000]}");time.sleep(.3)
		return _G.join(B)
def инспектировать_url(url,глубина=_L):
	A=url
	if any(A.endswith(B)for B in('.json','.xml','.csv','.txt','.md')):B=_получить_страницу(A);return f"Content of {A}:\n{B[:10000]}"if B else f"Could not fetch: {A}"
	return глубокий_анализ_сайта(A,глубина)