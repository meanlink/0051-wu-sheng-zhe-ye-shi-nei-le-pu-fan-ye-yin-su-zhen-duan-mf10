from grade_gate import split
from logistic import design,fit,loss,predict
from folio_registry import sheet,event_rows

def grade(cx,piece):
    learned,checked=split(event_rows(cx,piece))
    base,combined=fit(learned,False),fit(learned,True)
    base_loss=loss(base,checked,False)
    full_loss=loss(combined,checked,True)
    selected=base_loss-full_loss>=.015
    result=cx.execute("INSERT INTO turn_models VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *",
        (piece,"lead_hands" if selected else "lead",base_loss,full_loss,combined if selected else base,len(learned),len(checked))).fetchone()
    cx.execute("UPDATE turn_pieces SET stage='graded' WHERE code=%s",(piece,))
    return result

def view(cx,piece):
    plan=sheet(cx,piece)
    model=cx.execute("SELECT * FROM turn_models WHERE piece=%s",(piece,)).fetchone()
    baseline=round(risk(model,plan["legacy_lead"],plan["legacy_hands_busy"]),6) if model else None
    return {"stage":plan["stage"],"model":model,"baseline_risk":baseline}

def risk(model,lead,hands_busy):
    return predict(model["coef"],design(lead,hands_busy,model["method"]=="lead_hands"))
