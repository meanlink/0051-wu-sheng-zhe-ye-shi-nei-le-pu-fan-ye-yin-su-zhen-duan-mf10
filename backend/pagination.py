from fastapi import HTTPException
from folio_registry import sheet
from grade_models import risk,view

def place(cx,piece,data):
    plan=sheet(cx,piece,True)
    if plan["stage"]!="graded":
        raise HTTPException(409,"回验后、发谱前方可登记新版分页")
    if (data.target_page==plan["legacy_page"] and data.lead==plan["legacy_lead"] and data.hands_busy==plan["legacy_hands_busy"]):
        raise HTTPException(409,"拟改版须提供可区分的分页或翻页位置")
    evidence=view(cx,piece)["model"]
    return cx.execute("INSERT INTO turn_revisions VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *",
       (piece,data.code,data.target_page,data.lead,data.hands_busy,data.trial_passes,risk(evidence,data.lead,data.hands_busy))).fetchone()

def read(cx,piece):
    sheet(cx,piece)
    return {"revisions":cx.execute("SELECT * FROM turn_revisions WHERE piece=%s ORDER BY code",(piece,)).fetchall(),
      "release":cx.execute("SELECT * FROM turn_release WHERE piece=%s",(piece,)).fetchone()}
