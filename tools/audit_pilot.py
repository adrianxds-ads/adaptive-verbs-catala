import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
campaign = json.loads((ROOT / "campaign-01.json").read_text(encoding="utf-8"))
persons = ["1SG", "2SG", "3SG", "1PL", "2PL", "3PL"]

expected = {
    "parlar": {
        "indicatiu_present": ["parlo","parles","parla","parlem","parleu","parlen"],
        "subjuntiu_present": ["parli","parlis","parli","parlem","parleu","parlin"],
        "subjuntiu_imperfet": ["parlés","parlessis","parlés","parléssim","parléssiu","parlessin"],
    },
    "perdre": {
        "indicatiu_present": ["perdo","perds","perd","perdem","perdeu","perden"],
        "subjuntiu_present": ["perdi","perdis","perdi","perdem","perdeu","perdin"],
        "subjuntiu_imperfet": ["perdés","perdessis","perdés","perdéssim","perdéssiu","perdessin"],
    },
    "dormir": {
        "indicatiu_present": ["dormo","dorms","dorm","dormim","dormiu","dormen"],
        "subjuntiu_present": ["dormi","dormis","dormi","dormim","dormiu","dormin"],
        "subjuntiu_imperfet": ["dormís","dormissis","dormís","dormíssim","dormíssiu","dormissin"],
    },
    "servir": {
        "indicatiu_present": ["serveixo","serveixes","serveix","servim","serviu","serveixen"],        "subjuntiu_present": ["serveixi","serveixis","serveixi","servim","serviu","serveixin"],
        "subjuntiu_imperfet": ["servís","servissis","servís","servíssim","servíssiu","servissin"],
    },
    "anar": {
        "indicatiu_present": ["vaig","vas","va","anem","aneu","van"],
        "subjuntiu_present": ["vagi","vagis","vagi","anem","aneu","vagin"],
        "subjuntiu_imperfet": ["anés","anessis","anés","anéssim","anéssiu","anessin"],
    },
    "fer": {
        "indicatiu_present": ["faig","fas","fa","fem","feu","fan"],
        "subjuntiu_present": ["faci","facis","faci","fem","feu","facin"],
        "subjuntiu_imperfet": ["fes","fessis","fes","féssim","féssiu","fessin"],
    },
    "tenir": {
        "indicatiu_present": ["tinc","tens","té","tenim","teniu","tenen"],
        "subjuntiu_present": ["tingui","tinguis","tingui","tinguem","tingueu","tinguin"],
        "subjuntiu_imperfet": ["tingués","tinguessis","tingués","tinguéssim","tinguéssiu","tinguessin"],
    },
    "poder": {
        "indicatiu_present": ["puc","pots","pot","podem","podeu","poden"],
        "subjuntiu_present": ["pugui","puguis","pugui","puguem","pugueu","puguin"],
        "subjuntiu_imperfet": ["pogués","poguessis","pogués","poguéssim","poguéssiu","poguessin"],
    },
    "voler": {
        "indicatiu_present": ["vull","vols","vol","volem","voleu","volen"],
        "subjuntiu_present": ["vulgui","vulguis","vulgui","vulguem","vulgueu","vulguin"],
        "subjuntiu_imperfet": ["volgués","volguessis","volgués","volguéssim","volguéssiu","volguessin"],
    },
    "veure": {
        "indicatiu_present": ["veig","veus","veu","veiem","veieu","veuen"],
        "subjuntiu_present": ["vegi","vegis","vegi","vegem","vegeu","vegin"],
        "subjuntiu_imperfet": ["veiés","veiessis","veiés","veiéssim","veiéssiu","veiessin"],
    },
}

errors = []
questions = campaign.get("questions", [])
if len(questions) != 180:
    errors.append(f"question_count={len(questions)} expected=180")
if len({q.get("formId") for q in questions}) != len(questions):
    errors.append("duplicate formId")
if len({q.get("id") for q in questions}) != len(questions):
    errors.append("duplicate numeric id")

by_key = {(q["lemma"], q["tenseId"], q["personCode"]): q for q in questions}
for lemma, paradigms in expected.items():
    for tense_id, forms in paradigms.items():
        for person, canonical in zip(persons, forms):
            q = by_key.get((lemma, tense_id, person))
            if not q:
                errors.append(f"missing {lemma}|{tense_id}|{person}")
                continue
            if q.get("canonicalForm") != canonical:
                errors.append(f"canonical mismatch {lemma}|{tense_id}|{person}: {q.get('canonicalForm')} != {canonical}")
            opts = q.get("a") or []
            if len(opts) != 4 or len(set(opts)) != 4:
                errors.append(f"bad options {q.get('formId')}: {opts}")
            if q.get("c") not in range(4) or opts[q["c"]] != canonical:
                errors.append(f"correct option mismatch {q.get('formId')}")
            if len(q.get("optionMeta") or []) != 4:
                errors.append(f"optionMeta mismatch {q.get('formId')}")
            if q.get("auditStatus") != "AUDITED_CENTRAL":
                errors.append(f"auditStatus missing {q.get('formId')}")

required = {"formId","lemma","tenseId","tenseLabel","mood","tense","personCode","personLabel","canonicalForm","retrievalMode"}
for q in questions:
    missing = sorted(required - set(q))
    if missing:
        errors.append(f"missing fields {q.get('id')}: {missing}")

if errors:
    print("AUDIT FAILED")
    for error in errors:
        print("-", error)
    raise SystemExit(1)

print("AUDIT OK")
print(f"{len(questions)} canonical forms validated")
print("10 verbs × 3 paradigms × 6 persons")
print("All questions have 4 unique options and aligned metadata")
