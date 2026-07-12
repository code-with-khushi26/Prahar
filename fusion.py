import sqlite3
import json
from datetime import datetime
 
DB_PATH = "database/prahar.db"
 
 
def _determine_severity(kb_matches):
    """Simple severity rule: flagged + matches = HIGH, else LOW."""
    if kb_matches:
        return "HIGH"
    return "LOW"
 
 
def save_alert(module, raw_result, enriched_context, severity):
    """Insert an alert record into the alerts table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (timestamp, module, severity, raw_result, enriched_context)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        module,
        severity,
        json.dumps(raw_result),
        json.dumps(enriched_context),
    ))
    conn.commit()
    conn.close()
 
 
def get_all_alerts():
    """Fetch all stored alerts, most recent first."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, module, severity, raw_result, enriched_context FROM alerts ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "timestamp": r[1],
            "module": r[2],
            "severity": r[3],
            "raw_result": json.loads(r[4]),
            "enriched_context": json.loads(r[5]) if r[5] else None,
        }
        for r in rows
    ]
 
 
def _lookup_kb(term):
    """Search the DefenseKB weapons table for a matching term."""
    if not term:
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM weapons
        WHERE name LIKE ? OR type LIKE ? OR description LIKE ?
    """, (f"%{term}%", f"%{term}%", f"%{term}%"))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "type": r[2], "country": r[3], "description": r[4]}
        for r in rows
    ]
 
 
def _extract_terms(module, alert):
    """Pull out the term(s) worth checking against DefenseKB for each module type."""
    terms = []
 
    if module == "image":
        # single detection dict, or a list of them
        detections = alert if isinstance(alert, list) else [alert]
        for det in detections:
            if det.get("class"):
                terms.append(det["class"])
 
    elif module == "text":
        for ent in alert.get("entities", []):
            if ent.get("type") in ("ORG", "MISC"):
                terms.append(ent["word"])
 
    elif module == "audio":
        if alert.get("predicted_class"):
            terms.append(alert["predicted_class"])
 
    elif module == "video":
        # deepfake alerts usually don't map to weapon names directly,
        # but kept here in case labels reference equipment/org names
        if alert.get("final_label") == "FAKE":
            terms.append("deepfake")
 
    return terms
 
 
def enrich_alert(module, alert):
    """
    Takes a module name ('image', 'text', 'audio', 'video') and its raw
    alert/output, looks up relevant terms in DefenseKB, and returns the
    alert enriched with any matches.
    """
    terms = _extract_terms(module, alert)
 
    kb_matches = {}
    for term in terms:
        matches = _lookup_kb(term)
        if matches:
            kb_matches[term] = matches
 
    return {
        "module": module,
        "original_alert": alert,
        "kb_matches": kb_matches,
        "flagged": len(kb_matches) > 0,
        "severity": _determine_severity(kb_matches),
    }