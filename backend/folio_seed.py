from grade_models import grade

def seed(cx):
    for piece,title in [('FS-12','雨后的桥'),('FS-11','北窗四重奏'),('FS-10','黄昏分谱旧档')]:
        if not cx.execute("""INSERT INTO turn_pieces(code,title,part,legacy_page,legacy_lead,legacy_hands_busy)
           VALUES (%s,%s,'中提琴',6,1,true) ON CONFLICT DO NOTHING RETURNING code""",(piece,title)).fetchone():continue
        for sample,stem,lead_seconds in [('fit','A',[1,2,4,5,3,2]),('check','B',[1,2,3])]:
            if piece=='FS-11' and sample=='check':continue
            for number,lead in enumerate(lead_seconds,1):
                for hand in (False,True):
                    event=f"{stem}{number}-{int(hand)}"
                    miss=hand and (number<5 or sample=='check')
                    cx.execute("INSERT INTO turn_events VALUES (%s,%s,%s,%s,%s,%s)",(piece,event,sample,lead,hand,miss))
        if piece=='FS-10':
            grade(cx,piece)
