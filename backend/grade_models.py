from grade_gate import split
from logistic import design, fit, loss, predict
from folio_registry import sheet, event_rows


def grade(cx, piece, evidence_version):
    """对指定证据批次做回验。过期批次只留历史结论，不覆盖当前结论与校样。"""
    plan = sheet(cx, piece, True)
    learned, checked = split(event_rows(cx, piece))
    base, combined = fit(learned, False), fit(learned, True)
    base_loss = loss(base, checked, False)
    full_loss = loss(combined, checked, True)
    selected = base_loss - full_loss >= .015
    method = "lead_hands" if selected else "lead"
    coef = combined if selected else base
    model = cx.execute(
        """INSERT INTO turn_models
             (piece,method,lead_loss,combined_loss,coef,learned,checked,evidence_version)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
           ON CONFLICT(piece,evidence_version) DO UPDATE SET
             method=excluded.method, lead_loss=excluded.lead_loss,
             combined_loss=excluded.combined_loss, coef=excluded.coef,
             learned=excluded.learned, checked=excluded.checked
           RETURNING *""",
        (piece, method, base_loss, full_loss, coef, len(learned), len(checked), evidence_version),
    ).fetchone()

    latest = plan["evidence_version"] == evidence_version
    if latest:
        # 最新证据：待签校样的旧风险结论立即失效，按新模型重算并指向当前批次。
        for revision in cx.execute(
            "SELECT code,lead,hands_busy FROM turn_revisions WHERE piece=%s", (piece,)
        ).fetchall():
            cx.execute(
                """UPDATE turn_revisions
                   SET failure_probability=%s,basis_version=%s WHERE piece=%s AND code=%s""",
                (risk(model, revision["lead"], revision["hands_busy"]),
                 evidence_version, piece, revision["code"]),
            )
        if plan["stage"] != "released":
            # 最新证据回验完成：未发谱分谱进入待改谱（种子直接回验也走这里）。
            cx.execute("UPDATE turn_pieces SET stage='graded' WHERE code=%s", (piece,))
    return model | {"latest": latest, "current_evidence_version": plan["evidence_version"]}


def latest_model(cx, piece):
    return cx.execute(
        "SELECT * FROM turn_models WHERE piece=%s ORDER BY evidence_version DESC LIMIT 1",
        (piece,),
    ).fetchone()


def view(cx, piece):
    plan = sheet(cx, piece)
    model = latest_model(cx, piece)
    baseline = round(risk(model, plan["legacy_lead"], plan["legacy_hands_busy"]), 6) if model else None
    return {
        "stage": plan["stage"],
        "model": model,
        "baseline_risk": baseline,
        "evidence_version": plan["evidence_version"],
    }


def risk(model, lead, hands_busy):
    return predict(model["coef"], design(lead, hands_busy, model["method"] == "lead_hands"))
