from decimal import Decimal

from fastapi import HTTPException
from folio_registry import sheet
from grade_models import latest_model, risk, view


def place(cx, piece, data):
    plan = sheet(cx, piece, True)
    if plan["stage"] != "graded":
        raise HTTPException(409, "回验后、发谱前方可登记新版分页")
    if (data.target_page == plan["legacy_page"] and data.lead == plan["legacy_lead"]
            and data.hands_busy == plan["legacy_hands_busy"]):
        raise HTTPException(409, "拟改版须提供可区分的分页或翻页位置")
    evidence = latest_model(cx, piece)
    if evidence is None:
        raise HTTPException(409, "回验结论尚未生成，暂不能登记校样")
    return cx.execute(
        """INSERT INTO turn_revisions
           (piece,code,target_page,lead,hands_busy,trial_passes,failure_probability,basis_version)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
        (piece, data.code, data.target_page, data.lead, data.hands_busy,
         data.trial_passes, risk(evidence, data.lead, data.hands_busy),
         evidence["evidence_version"]),
    ).fetchone()


def _signability(cx, piece, plan, release):
    """汇总当前能否签发以及每一条原因；发谱页面直接展示。"""
    reasons, blockers = [], []
    if release is not None:
        blockers.append("该分谱已发演出用谱，签核与依据已冻结")
        return {"can_sign": False, "reasons": blockers, "evidence_version": plan["evidence_version"]}
    if plan["stage"] != "graded":
        blockers.append("只有完成回验的分谱可以签演出用稿")
    revisions = cx.execute(
        "SELECT * FROM turn_revisions WHERE piece=%s ORDER BY code", (piece,)
    ).fetchall()
    if not revisions:
        blockers.append("尚未登记任何分页改版")
    current_version = plan["evidence_version"]
    stale = [r["code"] for r in revisions if r["basis_version"] < current_version]
    if stale:
        blockers.append(f"证据已更新到第 {current_version} 批，待签校样 {', '.join(stale)} 的风险结论已失效，等待重算")
    grade = view(cx, piece)
    baseline = grade["baseline_risk"]
    fresh = [r for r in revisions if r["basis_version"] == current_version]
    if fresh and baseline is not None:
        limit = min(Decimal(".450000"), Decimal(str(baseline)))
        for r in fresh:
            faults = []
            if r["trial_passes"] < 3:
                faults.append("试翻不足三次")
            if r["failure_probability"] > limit or r["failure_probability"] >= Decimal(str(baseline)):
                faults.append("风险未低于原谱或高于上限 0.45")
            if faults:
                reasons.append(f"{r['code']}：{'、'.join(faults)}")
            else:
                reasons.append(f"{r['code']}：满足签发门槛（风险 {r['failure_probability']}，三次试翻通过）")
    return {
        "can_sign": not blockers and any(
            r["trial_passes"] >= 3 and baseline is not None
            and r["failure_probability"] <= min(Decimal(".450000"), Decimal(str(baseline)))
            and r["failure_probability"] < Decimal(str(baseline))
            for r in fresh
        ),
        "reasons": blockers + reasons,
        "evidence_version": current_version,
        "baseline_risk": baseline,
    }


def read(cx, piece):
    plan = sheet(cx, piece)
    release = cx.execute(
        "SELECT * FROM turn_release WHERE piece=%s", (piece,)
    ).fetchone()
    return {
        "revisions": cx.execute(
            "SELECT * FROM turn_revisions WHERE piece=%s ORDER BY code", (piece,)
        ).fetchall(),
        "release": release,
        "signability": _signability(cx, piece, plan, release),
    }
