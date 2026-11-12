import math
from src.services.graph import adjacency
def pagerank(node_ids,edges,damping=.85,personalization=None,tol=1e-10,max_iter=1000):
 ids,out=adjacency(node_ids,edges);n=len(ids)
 if not math.isfinite(damping) or not 0<damping<1 or not math.isfinite(tol) or tol<=0 or not isinstance(max_iter,int) or max_iter<1:raise ValueError('PageRank参数无效')
 if personalization is not None and (not isinstance(personalization,dict) or set(personalization)-set(ids)):raise ValueError('个性化包含未知文献')
 weights=[1. if not personalization else personalization.get(k,0.) for k in ids]
 if any(not isinstance(x,(int,float)) or isinstance(x,bool) or not math.isfinite(x) or x<0 for x in weights) or not math.isfinite(sum(weights)) or sum(weights)<=0:raise ValueError('个性化必须有限非负且总和正')
 total=sum(weights);p=[x/total for x in weights];x=p[:];history=[];converged=False
 for step in range(1,max_iter+1):
  dangling=sum(x[i] for i,v in enumerate(out) if not v);y=[((1-damping)+damping*dangling)*v for v in p]
  for i,targets in enumerate(out):
   if targets:
    share=damping*x[i]/len(targets)
    for j in targets:y[j]+=share
  mass=sum(y)
  if not math.isfinite(mass) or mass<=0:raise ValueError('PageRank概率质量无效')
  y=[v/mass for v in y];residual=sum(abs(a-b) for a,b in zip(x,y));history.append({'iteration':step,'residual':residual,'probability_sum':sum(y),'dangling_mass':dangling});x=y
  if residual<tol:converged=True;break
 return {'scores':dict(zip(ids,x)),'personalization':dict(zip(ids,p)),'iterations':step,'converged':converged,'residual':residual,'probability_sum':sum(x),'history':history}
