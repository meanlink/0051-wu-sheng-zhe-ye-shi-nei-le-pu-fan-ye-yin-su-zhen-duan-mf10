from fastapi import APIRouter, Depends

from core import db, require
from correction_input import Correction
from correction_service import apply, history

router = APIRouter(prefix="/page-turns/{piece}/corrections")


@router.get("")
def ledger(piece: str, _=Depends(require())):
    with db() as cx:
        return {"corrections": history(cx, piece)}


@router.post("", status_code=202)
def correct(piece: str, body: Correction, _=Depends(require("operator"))):
    with db() as cx:
        return apply(cx, piece, body)
