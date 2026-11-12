import json,math
from src.models.entities import CitationPolicy
from src.utils import repository as repo
from src.utils.identity import new_id,now
def list_policies():return repo.all_rows('policies')
def normalize_weights(text,ids):
 try:weights=json.loads(text)
 except (ValueError,TypeError):raise ValueError('个性化JSON解析失败')
 if not isinstance(weights,dict) or set(weights)-set(ids):raise ValueError('权重需为已知文献ID到数值的对象')
 if any(isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or x<0 or x>1e9 for x in weights.values()):raise ValueError('权重须有限非负且≤1e9')
 if not weights:return {id:1/len(ids) for id in ids}
 total=sum(weights.values())
 if total<=0:raise ValueError('个性化权重总和须正')
 return {id:weights.get(id,0)/total for id in ids}
def create(data):
 d=repo.get('datasets',data.dataset_id);weights=normalize_weights(data.personalization_json,[n['id'] for n in d['nodes']])
 return repo.put('policies',CitationPolicy(new_id('pol'),data.name,data.dataset_id,data.damping,weights,data.tolerance,data.max_iter,now()))
