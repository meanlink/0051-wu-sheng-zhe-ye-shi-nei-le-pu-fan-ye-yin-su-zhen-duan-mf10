from fastapi import APIRouter,Depends
from core import db,require
from grade_gate import freeze
from grade_models import view

router=APIRouter(prefix="/page-turns/{piece}/grade")
@router.get("")
def current(piece:str,_=Depends(require())):
    with db() as cx:return view(cx,piece)
@router.post("",status_code=202)
def run(piece:str,_=Depends(require("reviewer"))):
    with db() as cx:return freeze(cx,piece)
