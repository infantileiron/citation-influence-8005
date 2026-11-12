from fastapi import APIRouter,Depends
from src.controllers import policy as controller
from src.schemas.entities import PolicyInput
from src.services.auth import current,editor
router=APIRouter(prefix='/policies',tags=['policies'])
@router.get('')
def list_items(user=Depends(current)):return controller.list_items()
@router.post('',status_code=201)
def create(data:PolicyInput,user=Depends(editor)):return controller.create(data)
