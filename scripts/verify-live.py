import json,re,secrets,hashlib,time,os
from pathlib import Path
import urllib.request
base=os.environ.get('VERIFY_URL','https://echelon-breakpoint-50221095849.us-central1.run.app')
root=Path(__file__).resolve().parents[1]
def request(path,method='GET',payload=None,auth=False):
 headers={'Content-Type':'application/json'}
 if auth: headers['Authorization']='Bearer '+token
 req=urllib.request.Request(base+path,data=json.dumps(payload).encode() if payload is not None else None,headers=headers,method=method)
 with urllib.request.urlopen(req,timeout=60) as r:return r.status,r.read()
status,html=request('/');assert status==200
assets={}
for name in re.findall(r'(?:src|href)="(/assets/[^\"]+\.(?:js|css))"',html.decode())+['/assets/clinic-module.glb','/assets/transit-module.glb','/assets/sentinel-sedan-lod.glb','/assets/recon-drone-lod.glb','/assets/npc-mara.glb','/assets/npc-rook.glb','/assets/npc-imani.glb','/assets/npc-echo.glb']:
 status,data=request(name);same=hashlib.sha256(data).digest()==hashlib.sha256((root/'dist'/name.lstrip('/')).read_bytes()).digest();assert same,name
 assets[name]={'status':status,'matches_build':same}
token=secrets.token_hex(32);evidence={}
for label,path,method,payload in [('session','/api/session','GET',None),('save','/api/save','PUT',{'save':{'position':[150,1.85,310],'health':92,'relays':[False]*3,'updated':int(time.time()*1000),'campaign':{'version':1,'signal':True,'roam':{'jobs':{'courier':'complete'},'choices':{'courier':'private'},'waypoint':'archive','vehicle':{'x':150,'z':300,'yaw':0}}}}}),('restore','/api/session','GET',None),('director','/api/director','POST',{'snapshot':{'health':92,'alert':65,'shots':12,'district':'market','relays':0,'choice':None,'visited':[]}})]:
 status,data=request(path,method,payload,True);evidence[label]={'status':status,'body':json.loads(data)}
assert evidence['restore']['body']['persistent'] and evidence['restore']['body']['save']['health']==92
assert evidence['restore']['body']['save']['position']==[150,1.85,310]
assert evidence['restore']['body']['save']['campaign']['roam']['jobs']['courier']=='complete'
assert evidence['director']['body']['source']=='gemini', evidence['director']
story=evidence['restore']['body']['save']['campaign']['story']
status,data=request('/api/cast','POST',{'snapshot':{**story,'signal':True,'choice':None,'health':92,'relays':0,'alert':20},'interaction':{'id':'mara','message':'What did your signature have to do with Iona disappearing?'}},True)
evidence['cast']={'status':status,'body':json.loads(data)}
assert evidence['cast']['body']['source']=='gemini',evidence['cast']
assert evidence['cast']['body']['characters'][0]['id']=='mara'
line=evidence['cast']['body']['characters'][0]['line'];story['cast']['mara']['memory']=[line];story['cast']['mara']['met']=True
checkpoint=evidence['restore']['body']['save'];checkpoint['campaign']['story']=story;checkpoint['updated']=int(time.time()*1000)
request('/api/save','PUT',{'save':checkpoint},True)
status,data=request('/api/session',auth=True);restored=json.loads(data);assert restored['save']['campaign']['story']['cast']['mara']['memory']==[line]
evidence['character_memory_restored']=True
(root/'backend-cloud-verification.json').write_text(json.dumps(evidence,indent=2)+'\n')
status,data=request('/asset-shortlist.html');assert status==200 and b'60,601' in data
report={'url':base,'update':'Open City: connected districts, arcade driving, map waypoints and persistent NPC story jobs','assets':assets,'cloud_director':evidence['director']['body']['source'],'persistent_save_verified':True,'cast_model':'gemini','character_memory_verified':True}
(root/'deployment-status.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
