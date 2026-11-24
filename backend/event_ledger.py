from fastapi import HTTPException
from folio_registry import sheet

def register(cx,piece,data):
    if sheet(cx,piece,True)["stage"]!="recording":
        raise HTTPException(409,"回验数据已冻结")
    old=cx.execute("SELECT sample FROM turn_events WHERE piece=%s AND event=%s",(piece,data.event)).fetchone()
    if old and old["sample"]!=data.sample:
        raise HTTPException(409,"同一翻页事件不能在训练与验证批之间迁移")
    return cx.execute("""
      INSERT INTO turn_events VALUES (%s,%s,%s,%s,%s,%s)
      ON CONFLICT(piece,event) DO UPDATE SET lead=excluded.lead,hands_busy=excluded.hands_busy,missed=excluded.missed
      RETURNING *
    """,(piece,data.event,data.sample,data.lead,data.hands_busy,data.missed)).fetchone()
