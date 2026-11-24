from fastapi import APIRouter,Depends
from core import db,require
from pagination import place,read
from programme_release import sign
from revision_input import Release,Revision

router=APIRouter(prefix="/page-turns/{piece}/revisions")
@router.get("")
def archive(piece:str,_=Depends(require())):
    with db() as cx:return read(cx,piece)
@router.post("",status_code=201)
def propose(piece:str,body:Revision,_=Depends(require("operator"))):
    with db() as cx:return place(cx,piece,body)
@router.post("/release",status_code=201)
def confirm(piece:str,body:Release,user=Depends(require("reviewer"))):
    with db() as cx:return sign(cx,piece,body,user["email"])
