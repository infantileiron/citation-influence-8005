import json,hashlib
from src.models.entities import InfluenceStudy
from src.utils import repository as repo
from src.utils.identity import new_id,now
def list_studies():return [{k:v for k,v in s.items() if k!='snapshot'} for s in repo.all_rows('studies')]
def lock_snapshot(dataset,policy):
 if policy['dataset_id']!=dataset['id']:raise ValueError('口径必须属于该引文数据集')
 snapshot={'nodes':dataset['nodes'],'edges':dataset['edges'],'policy':{k:policy[k] for k in ('id','name','damping','personalization','tolerance','max_iter')},'direction':'citing_to_cited','dataset_name':dataset['name'],'source':dataset['source']}
 checksum=hashlib.sha256(json.dumps(snapshot,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest();return snapshot,checksum
def create(data):
 d=repo.get('datasets',data.dataset_id);p=repo.get('policies',data.policy_id);snapshot,checksum=lock_snapshot(d,p)
 return repo.put('studies',InfluenceStudy(new_id('study'),data.name,data.dataset_id,data.policy_id,snapshot,checksum,now()))
