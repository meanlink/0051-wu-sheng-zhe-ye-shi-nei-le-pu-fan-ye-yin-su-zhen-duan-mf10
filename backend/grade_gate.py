from fastapi import HTTPException
from core import enqueue
from folio_registry import sheet,event_rows

def split(rows):
    return ([r for r in rows if r["sample"]=="fit"],[r for r in rows if r["sample"]=="check"])

def freeze(cx,piece):
    if sheet(cx,piece,True)["stage"]!="recording":
        raise HTTPException(409,"该谱已冻结回验")
    learned,checked=split(event_rows(cx,piece))
    if len(learned)<8 or len(checked)<4 or any(len({r["missed"] for r in partition})<2 for partition in (learned,checked)):
        raise HTTPException(409,"训练与验证批各需两种结果，训练至少八笔、验证至少四笔")
    cx.execute("UPDATE turn_pieces SET stage='frozen' WHERE code=%s",(piece,))
    return {"job_id":enqueue(cx,"grade_turn_factors",{"piece":piece})}
