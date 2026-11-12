from src.services.pagerank import pagerank
from src.services.hits import hits
def analyze(snapshot,checksum):
 nodes=snapshot['nodes'];edges=snapshot['edges'];ids=[n['id'] for n in nodes];p=snapshot['policy'];pr=pagerank(ids,edges,p['damping'],p['personalization'],p['tolerance'],p['max_iter']);hi=hits(ids,edges,p['tolerance'],p['max_iter'])
 rows=[]
 for n in nodes:
  id=n['id'];rows.append({**n,'pagerank':pr['scores'][id],'hub':hi['hub'][id],'authority':hi['authority'][id],'in_degree':sum(t==id for s,t in edges),'out_degree':sum(s==id for s,t in edges),'personalization':pr['personalization'][id]})
 for key in ('pagerank','hub','authority'):
  for rank,row in enumerate(sorted(rows,key=lambda r:(-r[key],r['id'])),1):row[key+'_rank']=rank
 outgoing={s for s,t in edges};incident=set(sum(edges,[]));unseen=set(ids);components=[]
 while unseen:
  root=min(unseen);todo=[root];unseen.remove(root);part=[]
  while todo:
   k=todo.pop();part.append(k)
   for s,t in edges:
    j=t if s==k else s if t==k else None
    if j in unseen:unseen.remove(j);todo.append(j)
  components.append(sorted(part))
 return {'rows':sorted(rows,key=lambda r:r['pagerank_rank']),'edges':edges,'node_count':len(ids),'edge_count':len(edges),'dangling_count':len(set(ids)-outgoing),'isolated_count':len(set(ids)-incident),'components':components,'pagerank':pr,'hits':hi,'policy':p,'source':snapshot['source'],'checksum':checksum,'direction':snapshot['direction'],'limitations':['引文者→被引者；重复边和自引边拒绝，未使用时间衰减','PageRank为概率分布，HITS两向量L2归一，不可当概率','仅模拟网络内结构排名，不代表论文质量或因果影响','HITS重特征方向非唯一时排序依赖初始化；未收敛须人工复核']}
