from dataclasses import dataclass,field
from typing import Any
@dataclass
class CitationDataset:
 id:str
 name:str
 source:str
 nodes:list[dict]
 edges:list[list[str]]
 created_at:str=''
@dataclass
class CitationPolicy:
 id:str
 name:str
 dataset_id:str
 damping:float
 personalization:dict[str,float]
 tolerance:float
 max_iter:int
 created_at:str=''
@dataclass
class InfluenceStudy:
 id:str
 name:str
 dataset_id:str
 policy_id:str
 snapshot:dict
 checksum:str
 created_at:str=''
@dataclass
class InfluenceRun:
 id:str
 study_id:str
 status:str='queued'
 result:dict[str,Any]=field(default_factory=dict)
 error:str=''
 created_at:str=''
@dataclass
class CitationReview:
 id:str
 run_id:str
 comment:str
 status:str='pending'
 reviewer:str=''
 created_at:str=''
@dataclass
class Report:
 id:str
 run_id:str
 review_id:str
 title:str
 created_at:str=''
 ledger:bool=False
