import csv,io
from fastapi import HTTPException
from src.models.entities import Report
from src.config.settings import ARTIFACT_DIR
from src.utils import repository as repo
from src.utils.identity import new_id,now
def safe_cell(v):return "'"+v if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')) else v
def list_reports():return repo.all_rows('reports')
def create(data):
 run,review=repo.get('runs',data.run_id),repo.get('reviews',data.review_id)
 if review['status']!='approved' or review['run_id']!=run['id'] or run['status']!='completed':raise ValueError('报告必须引用该运行批准复核')
 report=repo.put('reports',Report(new_id('rpt'),data.run_id,data.review_id,data.title,now()));ARTIFACT_DIR.mkdir(parents=True,exist_ok=True);(ARTIFACT_DIR/(report['id']+'.csv')).write_text(download(report['id']),encoding='utf-8');return report
def download(id):
 report=repo.get('reports',id);run=repo.get('runs',report['run_id']);r=run['result'];review=repo.get('reviews',report['review_id'])
 if review['status']!='approved':raise HTTPException(403,'复核未通过')
 out=io.StringIO();w=csv.writer(out);w.writerow(['report','edge_direction','checksum','damping','pagerank_sum','pr_converged','hits_converged','hits_non_unique','hits_degenerate']);w.writerow([safe_cell(report['title']),r['direction'],r['checksum'],r['policy']['damping'],r['pagerank']['probability_sum'],r['pagerank']['converged'],r['hits']['converged'],r['hits']['non_unique'],r['hits']['degenerate']]);w.writerow([])
 fields=['id','title','year','area','in_degree','out_degree','personalization','pagerank','pagerank_rank','hub','hub_rank','authority','authority_rank'];w.writerow(fields)
 for row in r['rows']:w.writerow([safe_cell(row[k]) for k in fields])
 w.writerow([]);w.writerow(['citing','cited'])
 for edge in r['edges']:w.writerow(edge)
 return '\ufeff'+out.getvalue()
