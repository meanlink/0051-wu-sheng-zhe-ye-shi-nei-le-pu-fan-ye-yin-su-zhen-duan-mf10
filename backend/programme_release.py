from decimal import Decimal

from fastapi import HTTPException
from folio_registry import sheet
from grade_models import latest_model, view


def sign(cx, piece, body, user):
    plan = sheet(cx, piece, True)
    if plan["stage"] != "graded":
        raise HTTPException(409, "只有完成回验的分谱可以签演出用稿")
    revision = cx.execute(
        "SELECT * FROM turn_revisions WHERE piece=%s AND code=%s FOR UPDATE",
        (piece, body.revision),
    ).fetchone()
    if revision is None:
        raise HTTPException(404, "拟改分页未登记")

    current_version = plan["evidence_version"]
    if revision["basis_version"] < current_version:
        raise HTTPException(
            409,
            f"该校样依据的第 {revision['basis_version']} 批回验已过期，"
            f"当前为第 {current_version} 批证据，请等待按最新证据重算后再签",
        )
    if revision["trial_passes"] < 3:
        raise HTTPException(409, "改版需三次连续试翻成功")

    grade = view(cx, piece)
    baseline = Decimal(str(grade["baseline_risk"]))
    probability_limit = min(Decimal(".450000"), baseline)
    risk = revision["failure_probability"]
    if risk > probability_limit or risk >= baseline:
        raise HTTPException(409, "改版风险必须下降且不高于允许上限 0.45")

    model = latest_model(cx, piece)
    row = cx.execute(
        """INSERT INTO turn_release
             (piece,revision,programme,signer,basis_version,signed_risk,model_method)
           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
        (piece, body.revision, body.programme, user,
         current_version, risk, model["method"] if model else None),
    ).fetchone()
    cx.execute("UPDATE turn_pieces SET stage='released' WHERE code=%s", (piece,))
    return row
