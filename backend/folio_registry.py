from fastapi import HTTPException

def sheet(cx,piece,lock=False):
    row=cx.execute("SELECT * FROM turn_pieces WHERE code=%s"+(" FOR UPDATE" if lock else ""),(piece,)).fetchone()
    if row is None: raise HTTPException(404,"分谱不存在")
    return row

def event_rows(cx,piece):
    sheet(cx,piece)
    return cx.execute("SELECT * FROM turn_events WHERE piece=%s ORDER BY sample,event",(piece,)).fetchall()
