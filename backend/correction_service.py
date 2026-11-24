"""封存后的证据更正。

规则：
- 仅 frozen/graded/released 阶段可更正；实录阶段仍走事件登记接口。
- 按原事件编号更正，事件不能在训练/验证批之间迁移。
- 每批有效更正推进 evidence_version，待签校样的风险结论立即失效并排队重算。
- 同一 request_id 重试不重复落库、不重复排队；回验途中只保留一个任务并刷新到最新证据。
- 已发演出用谱的签核与依据是快照，不受后续更正影响。
"""
import json

from fastapi import HTTPException

from folio_registry import sheet

CORRECTABLE_STAGES = ("frozen", "graded", "released")


def _job(cx, piece, status):
    return cx.execute(
        """SELECT id,status FROM app_jobs
           WHERE kind='grade_turn_factors' AND payload->>'piece'=%s AND status=%s
           ORDER BY id DESC LIMIT 1"""
        + (" FOR UPDATE SKIP LOCKED" if status == "queued" else ""),
        (piece, status),
    ).fetchone()


def schedule_regrade(cx, piece, version):
    """保证该分谱最多一个排队回验任务，且任务始终指向最新证据版本。

    - 已有排队任务：把它的证据版本刷新为最新，不新增任务；
    - 仅有正在运行的任务：补一个排队任务（运行中的任务完成后可能已过期）；
    - 没有待处理任务：新建排队任务。
    """
    from core import enqueue
    payload = json.dumps({"piece": piece, "evidence_version": version})
    queued = _job(cx, piece, "queued")
    if queued is not None:
        cx.execute("UPDATE app_jobs SET payload=%s::jsonb WHERE id=%s", (payload, queued["id"]))
        return queued["id"]
    return enqueue(cx, "grade_turn_factors", {"piece": piece, "evidence_version": version})


def apply(cx, piece, data):
    plan = sheet(cx, piece, True)
    if plan["stage"] not in CORRECTABLE_STAGES:
        raise HTTPException(409, "实录阶段请直接登记翻页事件；封存后方可按原编号更正")

    duplicate = cx.execute(
        "SELECT * FROM event_corrections WHERE piece=%s AND event=%s AND request_id=%s",
        (piece, data.event, data.request_id),
    ).fetchone()
    if duplicate is not None:
        # 同一更正重试：原样返回既有批次，不推进版本、不重复排队。
        queued = _job(cx, piece, "queued")
        return {
            "duplicate": True,
            "evidence_version": duplicate["evidence_version"],
            "job_id": queued["id"] if queued else None,
        }

    current = cx.execute(
        "SELECT sample,lead,hands_busy,missed FROM turn_events WHERE piece=%s AND event=%s FOR UPDATE",
        (piece, data.event),
    ).fetchone()
    if current is None:
        raise HTTPException(404, "原事件编号不存在，更正只能针对已登记的翻页事件")
    if current["sample"] != data.sample:
        raise HTTPException(409, "同一翻页事件不能在训练与验证批之间迁移")

    changed = (
        float(current["lead"]) != data.lead
        or current["hands_busy"] != data.hands_busy
        or current["missed"] != data.missed
    )
    next_version = plan["evidence_version"] + 1 if changed else plan["evidence_version"]
    cx.execute(
        """INSERT INTO event_corrections
           (piece,event,request_id,sample,lead,hands_busy,missed,evidence_version)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (piece, data.event, data.request_id, data.sample, data.lead,
         data.hands_busy, data.missed, next_version),
    )
    if not changed:
        return {"duplicate": False, "evidence_version": next_version, "job_id": None}

    cx.execute(
        """UPDATE turn_events SET lead=%s,hands_busy=%s,missed=%s
           WHERE piece=%s AND event=%s""",
        (data.lead, data.hands_busy, data.missed, piece, data.event),
    )
    cx.execute(
        "UPDATE turn_pieces SET evidence_version=%s,last_correction_at=now() WHERE code=%s",
        (next_version, piece),
    )
    # 已发谱：历史签核与依据冻结，只更新证据，不重开回验。
    job_id = None if plan["stage"] == "released" else schedule_regrade(cx, piece, next_version)
    return {"duplicate": False, "evidence_version": next_version, "job_id": job_id}


def history(cx, piece):
    sheet(cx, piece)
    return cx.execute(
        "SELECT * FROM event_corrections WHERE piece=%s ORDER BY id", (piece,)
    ).fetchall()
