from __future__ import annotations

# Usage (via TOOL: run_file, or directly):
# python search-all-web.py <search-query> [results-limit] [debug]
# "python" – "python3 -->> APPLIES TO THE SYSTEM
# Performs multi-source web search using DuckDuckGo, Wikipedia, GitHub, YouTube, and Bing.
# Returns structured results containing titles, URLs, sources, and descriptions.
#
# Arguments:
# <search-query>  – The search text or question.
# [results-limit] – Maximum number of results per source (default: 10).
# [debug]         – Enable debug information (optional).
#
# Use this tool when you need web information, websites, repositories, videos, articles, or references.

_J='application/json'
_I=False
_H='Accept'
_G='description'
_F='source'
_E='url'
_D='<[^>]+>'
_C='title'
_B='ok'
_A='html'
import re,json,html,urllib.parse
from typing import List,Dict,Optional,Any
import requests
зз=10
дд='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121 Safari/537.36'
тт={_H:'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Language':'en-US,en;q=0.9','User-Agent':дд}
def getlink(url,headers=None,timeout=20):
	D='code';C='error';A=headers
	if A is None:A={}
	A={**тт,**A}
	try:B=requests.get(url,headers=A,timeout=timeout,allow_redirects=True);return{_B:B.status_code<400,_A:B.text,C:None if B.status_code<400 else f"HTTP {B.status_code}",D:B.status_code}
	except requests.exceptions.RequestException as E:return{_B:_I,_A:'',C:str(E),D:0}
def getDescription(html_content):
	B=html_content
	if not B:return''
	A=re.search('<meta[^>]+name=["\\\']description["\\\'][^>]+content=["\\\']([^"\\\']+)["\\\']',B,re.I)
	if A:return html.unescape(A.group(1).strip())
	A=re.search('<meta[^>]+property=["\\\']og:description["\\\'][^>]+content=["\\\']([^"\\\']+)["\\\']',B,re.I)
	if A:return html.unescape(A.group(1).strip())
	return''
def result(title,url,html_sample=''):'Build a result dictionary similar to PHP version.';A=html_sample;B=urllib.parse.urlparse(url).netloc or'';C=html.unescape(re.sub(_D,'',title).strip());return{_C:C,_E:url,_F:B,_G:getDescription(A)if A else''}
def allweb(query,зз=зз):
	G=f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}";C=getlink(G);B=[]
	if not C[_B]:return B
	H=C[_A];I=re.compile('<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',re.I|re.S);D=set()
	for(J,K)in I.findall(H):
		A=html.unescape(J);E=re.search('uddg=([^&]+)',A)
		if not E and not re.search(r'class=[\"\'][^\"\']*result__a',H[max(0,H.find(J)-100):H.find(J)+len(J)+100],re.I):continue
		if E:A=urllib.parse.unquote(E.group(1))
		if not re.match('^https?://',A,re.I):continue
		F=re.sub(_D,'',K).strip()
		if len(F)<2:continue
		if A in D:continue
		L=getlink(A,timeout=10);B.append(result(F,A,L.get(_A,'')));D.add(A)
		if len(B)>=зз:break
	return B
def wikipedia(query,зз=зз):
	E=f"https://ar.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json";B=getlink(E,headers={_H:_J});A=[]
	if B[_B]:
		try:
			F=json.loads(B[_A])
			for G in F.get('query',{}).get('search',[]):
				C=G[_C];D=f"https://ar.wikipedia.org/wiki/{urllib.parse.quote(C.replace(" ","_"))}";H=getlink(D,timeout=10);A.append(result(C,D,H.get(_A,'')))
				if len(A)>=зз:break
		except(json.JSONDecodeError,KeyError):pass
	return A
def github(query,зз=зз):
	G=f"https://github.com/search?q={urllib.parse.quote(query)}";D=getlink(G);A=[]
	if not D[_B]:return A
	H=D[_A];I=re.compile('<a[^>]+href="/([^/]+/[^/"]+)"[^>]*>(.*?)</a>',re.I|re.S);E=set()
	for(F,J)in I.findall(H):
		if F.split('/')[0] in {'search','topics','collections','login','settings','features','orgs','sponsors'}:continue
		B=f"https://github.com/{F}"
		if B in E:continue
		C=re.sub(_D,'',J).strip()
		if not C:C=F
		K=getlink(B,timeout=10);A.append(result(C,B,K.get(_A,'')));E.add(B)
		if len(A)>=зз:break
	return A
def bing(query,зз=зз):
	F=f"https://www.bing.com/search?q={urllib.parse.quote(query)}";C=getlink(F);A=[]
	if not C[_B]:return A
	G=C[_A];H=re.compile('<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',re.I|re.S);D=set()
	for(I,J)in H.findall(G):
		B=html.unescape(I)
		if urllib.parse.urlparse(B).netloc.endswith('bing.com'):
			U=urllib.parse.parse_qs(urllib.parse.urlparse(B).query).get('u',[''])[0]
			if U.startswith('a1'):
				try:B=__import__('base64').urlsafe_b64decode(U[2:]+'='*((-len(U[2:]))%4)).decode()
				except (ValueError,UnicodeError):pass
		if B in D:continue
		E=re.sub(_D,'',J).strip()
		if not E:continue
		K=getlink(B,timeout=10);A.append(result(E,B,K.get(_A,'')));D.add(B)
		if len(A)>=зз:break
	return A
def youtube(query,зз=зз):
	E='youtube.com';D='YouTube video';L=f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}";F=getlink(L);B=[]
	if not F[_B]:return B
	M=F[_A];N=re.findall('watch\\?v=([A-Za-z0-9_\\-]{11})',M);G=set();H=[]
	for A in N:
		if A not in G:G.add(A);H.append(A)
	I=0
	for A in H:
		O=f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={A}&format=json";J=getlink(O,headers={_H:_J},timeout=10);C=f"https://www.youtube.com/watch?v={A}"
		if J[_B]:
			try:K=json.loads(J[_A]);P=K.get(_C,D);Q=K.get('author_name','');B.append({_C:P,_E:C,_F:E,_G:Q})
			except json.JSONDecodeError:B.append({_C:D,_E:C,_F:E,_G:''})
		else:B.append({_C:D,_E:C,_F:E,_G:''})
		I+=1
		if I>=зз:break
	return B
def search_all(query,зз=зз,debug=_I):
	B=зз;A=query;D={'duckduckgo':allweb(A,B),'wikipedia':wikipedia(A,B),'github':github(A,B),'youtube':youtube(A,B),'bing':bing(A,B)};C={'date':__import__('datetime').datetime.now().strftime('%Y-%m-%d'),'query':A,'results':D,'Telegram':'t.me/darku1'}
	if debug:C['_debug']={'notes':'Debug mode enabled. Tor/darkweb support removed in this build.'}
	return C
if __name__=='__main__':
	import sys
	args=sys.argv[1:]
	limit=10
	debug=False
	if args and args[-1].lower() in ('true','false','yes','no','debug'):
		debug=args.pop().lower() in ('true','yes','debug')
	if len(args)>1:
		try:limit=max(1,min(50,int(args[-1])));args.pop()
		except ValueError:pass
	q=' '.join(args)
	data=search_all(q,зз=limit,debug=debug)
	print(json.dumps(data,ensure_ascii=_I,indent=2))