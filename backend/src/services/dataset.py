from src.models.entities import CitationDataset
from src.services.graph import parse_graph
from src.utils import repository as repo
from src.utils.identity import new_id,now
def summary(d):
 return {k:v for k,v in d.items() if k not in ('nodes','edges')}|{'node_count':len(d['nodes']),'edge_count':len(d['edges']),'areas':sorted(set(n['area'] for n in d['nodes']))}
def list_datasets():return [summary(d) for d in repo.all_rows('datasets')]
def create(data):
 nodes,edges=parse_graph(data.graph_json)
 return repo.put('datasets',CitationDataset(new_id('ds'),data.name,data.source,nodes,edges,now()))
def rename(id,data):
 d=repo.get('datasets',id);d['name']=data.name;return repo.put('datasets',d)

def detail(id):return repo.get('datasets',id)
