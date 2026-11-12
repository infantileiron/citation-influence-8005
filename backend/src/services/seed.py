import random
from src.utils import repository as repo
from src.utils.identity import now
from src.utils.security import hash_password
from src.services.statistics import analyze
from src.services.study import lock_snapshot
def demo_graph():
 rng=random.Random(2401);topics=['材料谱系','方法论','开放知识'];nodes=[{'id':f'YL{i:02d}','title':f'{topics[(i-1)//16]} · 文献{i:02d}的证据与讨论','year':2010+i%16,'area':topics[(i-1)//16]} for i in range(1,49)];edges=set()
 # Two disconnected active components plus isolated YL47/YL48; YL45/YL46 have no outgoing.
 for lo,hi,target in [(1,33,130),(33,47,30)]:
  local=set()
  while len(local)<target:
   source=rng.randrange(lo,min(hi,45));dest=rng.randrange(lo,hi)
   if source!=dest:local.add((f'YL{source:02d}',f'YL{dest:02d}'))
  edges.update(local)
 return nodes,[list(e) for e in sorted(edges)]
def seed():
 repo.init_db()
 for role,name in [('admin','引文复核编辑'),('analyst','文献网络分析员'),('viewer','索引阅览员')]:
  email=f'{role}@yanlin.test';repo.put('users',{'id':email,'email':email,'name':name,'role':role,'password_hash':hash_password('Citation2026!')},insert_only=True)
 nodes,edges=demo_graph();d={'id':'ds-yanlin','name':'砚林48篇模拟引文索引','source':'yanlin_citations_202611.json','nodes':nodes,'edges':edges,'created_at':now()};repo.put('datasets',d,insert_only=True)
 p={'id':'policy-uniform','name':'均匀回流 · d=0.85','dataset_id':'ds-yanlin','damping':.85,'personalization':{n['id']:1/48 for n in nodes},'tolerance':1e-10,'max_iter':1000,'created_at':now()};repo.put('policies',p,insert_only=True)
 snapshot,checksum=lock_snapshot(d,p);study={'id':'study-index','name':'十一月引文网络口径锁定','dataset_id':d['id'],'policy_id':p['id'],'snapshot':snapshot,'checksum':checksum,'created_at':now()};repo.put('studies',study,insert_only=True)
 repo.put('runs',{'id':'run-demo','study_id':'study-index','status':'completed','result':analyze(snapshot,checksum),'error':'','created_at':now()},insert_only=True)
 repo.put('reviews',{'id':'review-demo','run_id':'run-demo','comment':'引用者到被引者方向、悬空回流与双向HITS归一口径核验通过。','status':'approved','reviewer':'admin@yanlin.test','created_at':now()},insert_only=True)
 repo.put('reports',{'id':'report-demo','run_id':'run-demo','review_id':'review-demo','title':'砚林文献十一月影响结构复核册','created_at':now()},insert_only=True)
 return {t:len(repo.all_rows(t)) for t in ('users','datasets','policies','studies','runs','reviews','reports')}
