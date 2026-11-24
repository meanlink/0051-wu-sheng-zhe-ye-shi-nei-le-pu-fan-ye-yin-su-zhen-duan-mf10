from fastapi import APIRouter,Depends
from core import db,require

router=APIRouter(prefix="/page-turns")
@router.get("")
def list_pieces(_=Depends(require())):
    with db() as cx: return cx.execute("SELECT * FROM turn_pieces ORDER BY code DESC").fetchall()
