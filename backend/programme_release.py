from decimal import Decimal
from fastapi import HTTPException
from folio_registry import sheet
from grade_models import view

def sign(cx,piece,body,user):
    if sheet(cx,piece,True)["stage"]!="graded":
        raise HTTPException(409,"只有完成回验的分谱可以签演出用稿")
    revision=cx.execute("SELECT * FROM turn_revisions WHERE piece=%s AND code=%s",(piece,body.revision)).fetchone()
    if revision is None: raise HTTPException(404,"拟改分页未登记")
    if revision["trial_passes"]<3:
        raise HTTPException(409,"改版需三次连续试翻成功")
    probability_limit=min(Decimal(".450000"), Decimal(str(view(cx,piece)["baseline_risk"])))
    risk=revision["failure_probability"]
    if risk>probability_limit or risk>=Decimal(str(view(cx,piece)["baseline_risk"])):
        raise HTTPException(409,"改版风险必须下降且不高于允许上限 0.45")
    row=cx.execute("INSERT INTO turn_release VALUES (%s,%s,%s,%s) RETURNING *",
                   (piece,body.revision,body.programme,user)).fetchone()
    cx.execute("UPDATE turn_pieces SET stage='released' WHERE code=%s",(piece,))
    return row
