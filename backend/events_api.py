from fastapi import APIRouter,Depends
from core import db,require
from event_ledger import register
from folio_registry import event_rows
from turn_inputs import Turn

router=APIRouter(prefix="/page-turns/{piece}/events")
@router.get("")
def records(piece:str,_=Depends(require())):
    with db() as cx: return event_rows(cx,piece)

@router.put("")
def append(piece:str,data:Turn,_=Depends(require("operator"))):
    with db() as cx: return register(cx,piece,data)
