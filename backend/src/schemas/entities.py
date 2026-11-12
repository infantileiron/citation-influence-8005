from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class InputModel(BaseModel):
 model_config=ConfigDict(allow_inf_nan=False)
class LoginInput(InputModel):
 email:str
 password:str
class DatasetInput(InputModel):
 name:str=Field(min_length=2,max_length=100)
 source:str=Field(default='yanlin_citations_202611.json',max_length=100)
 graph_json:str=Field(min_length=2,max_length=350000)
class RenameDataset(InputModel):
 name:str=Field(min_length=2,max_length=100)
class PolicyInput(InputModel):
 name:str=Field(min_length=2,max_length=100)
 dataset_id:str
 damping:float=Field(default=.85,gt=0,lt=1)
 personalization_json:str=Field(default='{}',max_length=20000)
 tolerance:float=Field(default=1e-10,ge=1e-14,le=1e-3)
 max_iter:int=Field(default=1000,ge=1,le=2000)
class InfluenceStudyInput(InputModel):
 name:str=Field(min_length=2,max_length=100)
 dataset_id:str
 policy_id:str
class RunInput(InputModel):
 study_id:str
class ReviewInput(InputModel):
 run_id:str
 comment:str=Field(min_length=5,max_length=2000)
class DecisionInput(InputModel):
 status:Literal['approved','rejected']
 comment:str=Field(min_length=5,max_length=2000)
class ReportInput(InputModel):
 run_id:str
 review_id:str
 title:str=Field(min_length=2,max_length=100)
