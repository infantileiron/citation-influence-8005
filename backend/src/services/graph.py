import json,math,re
from src.constants.domain import MAX_NODES,MAX_EDGES
def parse_graph(text):
 try:g=json.loads(text)
 except (TypeError,ValueError):raise ValueError('引文JSON解析失败，请修正后重试')
 if not isinstance(g,dict) or not isinstance(g.get('nodes'),list) or not isinstance(g.get('edges'),list):raise ValueError('需要nodes文献数组与edges引用数组')
 if not 1<=len(g['nodes'])<=MAX_NODES or len(g['edges'])>MAX_EDGES:raise ValueError('文献1—200篇，引用最多2000条')
 nodes=[];ids=set()
 for n in g['nodes']:
  if not isinstance(n,dict):raise ValueError('文献必须为对象')
  id=n.get('id');title=n.get('title');year=n.get('year',2020);area=n.get('area','未分组')
  if not isinstance(id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,30}',id) or id in ids:raise ValueError('文献ID须唯一且仅含字母数字下划线连字符')
  if not isinstance(title,str) or not title.strip() or len(title)>120:raise ValueError('文献标题不能为空，最多120字')
  if not isinstance(year,int) or isinstance(year,bool) or not 1900<=year<=2100 or not isinstance(area,str) or not 1<=len(area)<=30:raise ValueError('年份或领域无效')
  ids.add(id);nodes.append({'id':id,'title':title.strip(),'year':year,'area':area})
 edges=[];seen=set()
 for e in g['edges']:
  if not isinstance(e,list) or len(e)!=2 or not all(isinstance(k,str) and k in ids for k in e):raise ValueError('引用边必须为两个已知ID：[引用者,被引者]')
  if e[0]==e[1]:raise ValueError('本口径拒绝自引边')
  pair=tuple(e)
  if pair in seen:raise ValueError('重复引用边拒绝，不做隐式加权')
  seen.add(pair);edges.append(list(pair))
 return sorted(nodes,key=lambda n:n['id']),sorted(edges)
def adjacency(node_ids,edges):
 ids=list(node_ids)
 if not ids or len(ids)!=len(set(ids)):raise ValueError('算法需要非空唯一节点')
 index={id:i for i,id in enumerate(ids)};out=[[] for _ in ids];seen=set()
 for source,target in edges:
  if source not in index or target not in index or (source,target) in seen:raise ValueError('未知节点或重复边')
  seen.add((source,target));out[index[source]].append(index[target])
 return ids,out
