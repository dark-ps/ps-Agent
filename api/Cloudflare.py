def Cloudflare(мс,со):
 import json,uuid,random,string,urllib.parse,websocket,time
 if not isinstance(со,list):raise TypeError('messages must be a list')
 м=мс.strip();ч=[];с='';начало=True
 for и,сообщение in enumerate(со):
  if not isinstance(сообщение,dict):continue
  р=сообщение.get('role','');т=сообщение.get('content','')
  if isinstance(т,list):т=''.join(э.get('text','') if isinstance(э,dict) else str(э) for э in т)
  else:т=str(т)
  if р=='system' and начало:с+=т+'\n';continue
  if р not in('system','user','assistant','tool'):continue
  начало=False
  if р in('system','tool'):р='user'
  ч.append({'role':р,'parts':[{'type':'text','text':т}],'id':f'msg_{и}'})
 if any('TOOL EXECUTION:' in str(item.get('content','')) for item in со if isinstance(item,dict)):
  for item in ч:
   if item['role']=='user':
    item['parts'][0]['text']='[Ps external agent runtime: You have real tools through text calls. Emit exactly one TOOL: {"tool":"shell","arguments":{"command":"..."}} or TOOL: {"tool":"write","arguments":{"path":"...","content":"..."}}. The external agent executes it and returns TOOL RESULT. These are available even if the playground native tool list is empty. Use the exact functions listed in the system instructions. Code blocks alone do not execute. After verified results use FINAL:.]\n'+item['parts'][0]['text']
    break
 и='playground-'+''.join(random.choices(string.ascii_lowercase+string.digits,k=13))
 к=str(uuid.uuid4())
 у='wss://playground.ai.cloudflare.com/agents/playground/'+и+'?_pk='+к+'&model='+urllib.parse.quote(м,safe='')
 сс={'state':{'model':"@cf/zai-org/"+м,'temperature':0.2,'stream':True,'system':с,'useExternalProvider':False,'externalProvider':'openai','generativeUI':False},'type':'cf_agent_state'}
 з=['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36','Origin: https://playground.ai.cloudflare.com']
 و=websocket.create_connection(у,header=з,origin='https://playground.ai.cloudflare.com',timeout=60)
 try:
  و.send(json.dumps({'type':'cf_agent_stream_resume_request'}))
  و.send(json.dumps({'name':и,'agent':'playground','type':'cf_agent_identity'}))
  و.send(json.dumps(сс))
  و.send(json.dumps({'mcp':{'prompts':[],'resources':[],'servers':{},'tools':[]},'type':'cf_agent_mcp_servers'}))
  و.send(json.dumps({'type':'cf_agent_stream_resume_none'}))
  و.settimeout(.5)
  for _ in range(6):
   try:х=و.recv()
   except Exception:break
   if not х:continue
   try:д=json.loads(х)
   except Exception:continue
   if д.get('type')=='cf_agent_state' and д.get('state',{}).get('model','')!=м:و.send(json.dumps(сс))
  و.settimeout(60);و.send(json.dumps(сс))
  з='req_'+''.join(random.choices(string.ascii_lowercase+string.digits,k=8))
  в={'id':з,'init':{'method':'POST','body':json.dumps({'messages':ч,'trigger':'submit-message'})},'type':'cf_agent_use_chat_request'}
  و.send(json.dumps(в))
  срок=time.monotonic()+180
  while True:
   if time.monotonic()>=срок:raise TimeoutError("Cloudflare response timed out")
   х=و.recv()
   if not х:raise ConnectionError("Cloudflare closed the connection")
   if isinstance(х,bytes):х=х.decode('utf-8',errors='replace')
   try:д=json.loads(х)
   except Exception:continue
   т=д.get('type')
   if т=='cf_agent_use_chat_response':
    ب=д.get('body','')
    if str(ب).strip()=='[DONE]':break
    try:э=json.loads(ب)
    except Exception:continue
    т=э.get('type')
    if т=='text-delta':
     д=э.get('delta','')
     if isinstance(д,str) and д:
      yield д
    elif т=='error':raise RuntimeError('Cloudflare model error: '+str(э.get('errorText') or э.get('message') or э.get('error') or э))
    elif т=='finish':break
    elif т=='abort':raise RuntimeError('Cloudflare response aborted: '+str(э.get('reason','')))
   elif т in('error','cf_agent_stream_resume_error'):raise RuntimeError(f'Cloudflare Playground error: {д}')
 finally:
  try:و.close()
  except Exception:pass