import math
import numpy as np
from src.services.graph import adjacency
def hits(node_ids,edges,tol=1e-10,max_iter=1000):
 ids,out=adjacency(node_ids,edges);n=len(ids)
 if not math.isfinite(tol) or tol<=0 or not isinstance(max_iter,int) or max_iter<1:raise ValueError('HITS参数无效')
 A=np.zeros((n,n))
 for i,targets in enumerate(out):
  for j in targets:A[i,j]=1.
 singular=np.linalg.svd(A,compute_uv=False);top=float(singular[0]);multiplicity=int(np.sum(np.abs(singular-top)<=max(1e-12,top*1e-10))) if top>0 else n
 if top==0:return {'hub':dict.fromkeys(ids,0.),'authority':dict.fromkeys(ids,0.),'converged':False,'iterations':0,'residual':None,'hub_l2':0.,'authority_l2':0.,'degenerate':True,'non_unique':True,'top_singular_value':0.,'top_multiplicity':n,'history':[],'note':'无引用边，HITS无可归一方向；零向量不是排名概率'}
 h=np.ones(n)/math.sqrt(n);a=h.copy();history=[];converged=False
 for step in range(1,max_iter+1):
  anew=A.T@h;anorm=float(np.linalg.norm(anew));anew/=anorm
  hnew=A@anew;hnorm=float(np.linalg.norm(hnew));hnew/=hnorm
  residual=float(np.linalg.norm(anew-a)+np.linalg.norm(hnew-h));history.append({'iteration':step,'residual':residual});a,h=anew,hnew
  if residual<tol:converged=True;break
 non_unique=multiplicity>1
 return {'hub':dict(zip(ids,map(float,h))),'authority':dict(zip(ids,map(float,a))),'converged':converged,'iterations':step,'residual':residual,'hub_l2':float(np.linalg.norm(h)),'authority_l2':float(np.linalg.norm(a)),'degenerate':False,'non_unique':non_unique,'top_singular_value':top,'top_multiplicity':multiplicity,'history':history,'note':'最高奇异值重数>1：方向非唯一，当前为全正均匀初始化选取的方向' if non_unique else 'Hub与Authority分别L2归一，不是概率；全正均匀初始化'}
