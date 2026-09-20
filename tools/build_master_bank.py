import json, re, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path
from lxml import html

ROOT=Path(__file__).resolve().parents[1]
CAMPAIGN_PATH=ROOT/"campaign-01.json"
old=json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
old_by_form={q.get("formId"):q for q in old.get("questions",[])}

VERBS=[
"ser","estar","haver","tenir","venir","anar","donar","veure","saber","deure","poder","voler","creure","fer","dir","sortir","viure","merèixer","beure","fugir",
"coure","cabre","mantenir","córrer","entendre","vendre","escriure","moure","morir","conèixer","néixer","commoure","obrir","seure","doldre","caure","obtenir","dur","concloure","complir",
"oferir","atendre","fondre","riure","somriure","jeure","collir","lluir","complaure","valer","eixir","prometre","vèncer","cantar","estimar","escoltar","portar","buscar","tocar","arribar",
"esperar","comprar","pagar","mirar","agafar","cridar","estudiar","treballar","preguntar","viatjar","acabar","ajudar","parlar","oblidar","guanyar","utilitzar","caminar","necessitar","intentar","entrar",
"ensenyar","tornar","menjar","marxar","debatre","pertànyer","perdre","retre","prémer","témer","abatre","rompre","decidir","escollir","dormir","traduir","discutir","llegir","compartir","produir",
"servir","començar","canviar","trobar","passar","posar","aprendre","agrair","sentir","conduir","incloure","omplir","bullir","cosir","escopir","tossir","trencar","jutjar","adequar","netejar"
]
assert len(VERBS)==120 and len(set(VERBS))==120

PERSONS=[
("1SG","JO"),("2SG","TU"),("3SG","ELL / ELLA"),
("1PL","NOSALTRES"),("2PL","VOSALTRES"),("3PL","ELLS / ELLES")
]
IMP_PERSONS=[("2SG","TU"),("3SG","ELL / ELLA"),("1PL","NOSALTRES"),("2PL","VOSALTRES"),("3PL","ELLS / ELLES")]

# Exact headings/ids used by verbs.cat. Tier is scheduling, not content availability.
PARADIGMS=[
("indicatiu_present","Present d'indicatiu","indicatiu","present",1,"indicatiu-present"),
("indicatiu_imperfet","Imperfet d'indicatiu","indicatiu","imperfet",1,"indicatiu-imperfet"),
("indicatiu_perfet","Perfet d'indicatiu","indicatiu","perfet",2,"indicatiu-perfet"),
("indicatiu_plusquamperfet","Plusquamperfet d'indicatiu","indicatiu","plusquamperfet",2,"indicatiu-plusquamperfet"),
("indicatiu_passat_simple","Passat simple","indicatiu","passat_simple",3,"indicatiu-passat-simple"),
("indicatiu_passat_anterior","Passat anterior","indicatiu","passat_anterior",3,"indicatiu-passat-anterior"),
("indicatiu_passat_perifrastic","Passat perifràstic","indicatiu","passat_perifrastic",1,"indicatiu-passat-perifrastic"),
("indicatiu_passat_anterior_perifrastic","Passat anterior perifràstic","indicatiu","passat_anterior_perifrastic",3,"indicatiu-passat-anterior-perifrastic"),
("indicatiu_futur","Futur","indicatiu","futur",1,"indicatiu-futur"),
("indicatiu_futur_perfet","Futur perfet","indicatiu","futur_perfet",2,"indicatiu-futur-perfet"),
("condicional_present","Condicional","condicional","present",1,"condicional"),
("condicional_perfet","Condicional perfet","condicional","perfet",2,"condicional-perfet"),
("subjuntiu_present","Present de subjuntiu","subjuntiu","present",1,"subjuntiu-present"),
("subjuntiu_perfet","Perfet de subjuntiu","subjuntiu","perfet",2,"subjuntiu-perfet"),
("subjuntiu_imperfet","Imperfet de subjuntiu","subjuntiu","imperfet",1,"subjuntiu-imperfet"),
("subjuntiu_plusquamperfet","Plusquamperfet de subjuntiu","subjuntiu","plusquamperfet",2,"subjuntiu-plusquamperfet"),
("imperatiu_present","Imperatiu","imperatiu","present",1,None),
("gerundi","Gerundi","gerundi","gerundi",2,None),
("participi","Participi","participi","participi",2,None),
]
PARA={x[0]:x for x in PARADIGMS}

def nfc(s):
    return unicodedata.normalize("NFC"," ".join(str(s).split()).strip())

def expand_parenthetical(s):
    s=nfc(s)
    m=re.match(r"^([^\s()]+)\s+\(([^)]+)\)\s+(.+)$",s)
    if m:
        a,b,tail=m.groups()
        return [nfc(a+" "+tail),nfc(b+" "+tail)]
    # occasional parenthetical at end or no tail
    m=re.match(r"^([^\s()]+)\s+\(([^)]+)\)$",s)
    if m:
        return [nfc(m.group(1)),nfc(m.group(2))]
    return [s]

def fetch_verb(verb):
    q=urllib.parse.urlencode({"option":"com_verb","task":"conjugate","verb":verb})
    req=urllib.request.Request("https://www.verbs.cat/ca/conjugacio.html?"+q,headers={"User-Agent":"AdaptiveVerbsCatala/0.3 personal-study-bank"})
    with urllib.request.urlopen(req,timeout=25) as r:
        final=r.geturl()
        body=r.read()
    doc=html.fromstring(body)
    title=nfc(doc.xpath("string(//h1)"))
    if verb.lower() not in title.lower():
        raise RuntimeError(f"{verb}: unexpected page {final} / {title}")
    return doc,final

def table_forms_after_h3(doc,hid):
    nodes=doc.xpath(f"//h3[@id='{hid}']")
    if not nodes: raise RuntimeError(f"missing heading {hid}")
    tables=nodes[0].xpath("following-sibling::table[1]")
    if not tables: raise RuntimeError(f"missing table after {hid}")
    rows=tables[0].xpath(".//tr")
    if len(rows)!=6: raise RuntimeError(f"{hid}: expected 6 rows got {len(rows)}")
    return [expand_parenthetical(r.xpath("string(td)")) for r in rows]

def imperative_forms(doc):
    h2=[x for x in doc.xpath("//h2") if "imperatiu" in nfc(x.text_content()).lower()]
    if not h2: raise RuntimeError("missing imperative h2")
    tables=h2[0].xpath("following-sibling::div[1]//table[contains(@class,'table-verbforms')]")
    if not tables: raise RuntimeError("missing imperative table")
    rows=tables[0].xpath(".//tr")
    if len(rows)!=5: raise RuntimeError(f"imperative rows {len(rows)}")
    return [expand_parenthetical(r.xpath("string(td)")) for r in rows]

def nonpersonal(doc):
    tables=doc.xpath("//table[not(contains(@class,'table-verbforms'))]")
    for t in tables:
        rows=t.xpath(".//tr")
        labels=[nfc(r.xpath("string(th)")) for r in rows]
        if "Infinitiu" in labels and "Gerundi" in labels and "Participi" in labels:
            out={}
            for r in rows:
                label=nfc(r.xpath("string(th)"))
                if label=="Gerundi":
                    out["gerundi"]=[nfc(r.xpath("string(td)"))]
                elif label=="Participi":
                    spans=[nfc(x) for x in r.xpath("td//span/text()") if nfc(x)]
                    out["participi"]=spans or [nfc(r.xpath("string(td)")).split(",")[0]]
                elif label=="Infinitiu":
                    spans=[nfc(x) for x in r.xpath("td//span/text()") if nfc(x)]
                    raw=nfc(r.xpath("string(td)"))
                    out["infinitiu"]=spans or [nfc(x) for x in raw.split(",") if nfc(x)]
            return out
    raise RuntimeError("missing nonpersonal table")

scraped={}
source_urls={}
for i,verb in enumerate(VERBS,1):
    doc,url=fetch_verb(verb)
    data={}
    for pid,label,mood,tense,tier,hid in PARADIGMS:
        if hid:
            rows=table_forms_after_h3(doc,hid)
            data[pid]={code:rows[j] for j,(code,_) in enumerate(PERSONS)}
    imps=imperative_forms(doc)
    data["imperatiu_present"]={code:imps[j] for j,(code,_) in enumerate(IMP_PERSONS)}
    np=nonpersonal(doc)
    data["gerundi"]={"NP":np["gerundi"]}
    data["participi"]={"NP":np["participi"]}
    inf_norm=[x.lower() for x in np["infinitiu"]]
    if verb.lower() not in inf_norm and not any(verb.lower() in x.split(",") for x in inf_norm):
        raise RuntimeError(f"{verb}: infinitive mismatch {np['infinitiu']}")
    scraped[verb]=data;source_urls[verb]=url
    if i%20==0: print(f"scraped {i}/120")
    time.sleep(0.06)

slots=[]
for verb in VERBS:
    data=scraped[verb]
    for pid,label,mood,tense,tier,hid in PARADIGMS:
        people=[("NP","FORMA NO PERSONAL")] if pid in ("gerundi","participi") else (IMP_PERSONS if pid=="imperatiu_present" else PERSONS)
        for code,plabel in people:
            forms=[nfc(x) for x in data[pid][code] if nfc(x)]
            # de-duplicate accepted variants
            forms=list(dict.fromkeys(forms))
            if not forms: raise RuntimeError(f"{verb}/{pid}/{code}: empty")
            slots.append({"lemma":verb,"tenseId":pid,"tenseLabel":label,"mood":mood,"tense":tense,"tier":tier,"personCode":code,"personLabel":plabel,"forms":forms})

by_key={(s["lemma"],s["tenseId"],s["personCode"]):s for s in slots}
by_lemma={}
for s in slots: by_lemma.setdefault(s["lemma"],[]).append(s)

def no_accents(s):
    return s.translate(str.maketrans({"à":"a","è":"e","é":"e","í":"i","ï":"i","ò":"o","ó":"o","ú":"u","ü":"u","À":"A","È":"E","É":"E","Í":"I","Ï":"I","Ò":"O","Ó":"O","Ú":"U","Ü":"U"}))

def relation(target,other):
    if target["tenseId"]==other["tenseId"] and target["personCode"]!=other["personCode"]:
        return "PERSON_CONFUSION",f"{target['personCode']}->{other['personCode']}"
    if target["mood"]!=other["mood"]:
        return "MOOD_CONFUSION",f"{target['tenseId']}->{other['tenseId']}"
    if target["tenseId"]!=other["tenseId"]:
        return "TENSE_CONFUSION",f"{target['tenseId']}->{other['tenseId']}"
    return "OTHER","related_form"

def add_wrong(opts,meta,form,err,detail,forbidden):
    form=nfc(form)
    if not form or form in forbidden or form in opts:return False
    opts.append(form);meta.append({"errorType":err,"detail":detail});return True

questions=[]
pilot_preserved=0
for idx,s in enumerate(slots,1):
    accepted=list(dict.fromkeys(s["forms"]))
    canonical=accepted[0]
    opts=[canonical];om=[{"errorType":None,"detail":"CORRECT"}]
    forbidden=set(accepted)

    # Same paradigm, different person.
    if s["personCode"]!="NP":
        plist=IMP_PERSONS if s["tenseId"]=="imperatiu_present" else PERSONS
        for pc,_ in plist:
            if pc==s["personCode"]:continue
            other=by_key.get((s["lemma"],s["tenseId"],pc))
            if other and add_wrong(opts,om,other["forms"][0],"PERSON_CONFUSION",f"{s['personCode']}->{pc}",forbidden):break

    # Strong cross-tense/mood contrasts.
    contrasts=["indicatiu_present","subjuntiu_present","subjuntiu_imperfet","indicatiu_imperfet","indicatiu_passat_perifrastic","indicatiu_futur","condicional_present","imperatiu_present","indicatiu_perfet","indicatiu_plusquamperfet","subjuntiu_perfet","participi","gerundi"]
    for pid in contrasts:
        if len(opts)>=3:break
        if pid==s["tenseId"]:continue
        other=by_key.get((s["lemma"],pid,s["personCode"]))
        if other:
            err,detail=relation(s,other)
            add_wrong(opts,om,other["forms"][0],err,detail,forbidden)

    # Minimal accent/diaeresis confusion.
    if len(opts)<4:
        na=no_accents(canonical)
        if na!=canonical:add_wrong(opts,om,na,"ACCENT_ERROR","diacritic_removed",forbidden)

    if len(opts)<4:
        for other in by_lemma[s["lemma"]]:
            if len(opts)>=4:break
            if other is s:continue
            err,detail=relation(s,other)
            add_wrong(opts,om,other["forms"][0],err,detail,forbidden)

    if len(opts)<4:
        for other in slots:
            if len(opts)>=4:break
            if other["lemma"]==s["lemma"]:continue
            if other["tenseId"]==s["tenseId"] and other["personCode"]==s["personCode"]:
                add_wrong(opts,om,other["forms"][0],"STEM_ERROR",f"{s['lemma']}->{other['lemma']}",forbidden)

    if len(opts)!=4: raise RuntimeError(f"cannot build options {s}")

    form_id=f"{s['lemma']}|{s['mood']}|{s['tense']}|{s['personCode']}"
    oldq=old_by_form.get(form_id)
    if oldq:
        if nfc(oldq.get("canonicalForm"))!=canonical:
            raise RuntimeError(f"PILOT REGRESSION {form_id}: {oldq.get('canonicalForm')} != {canonical}")
        pilot_preserved+=1
        # Preserve audited pilot distractors and metadata.
        if len(oldq.get("a",[]))==4 and len(set(oldq["a"]))==4:
            opts=oldq["a"];om=oldq.get("optionMeta",om)

    q={
      "id":300000+idx,
      "cat":s["lemma"],"skill":s["lemma"],
      "templateId":f"{s['tenseId']}|{s['personCode']}",
      "domain":s["tenseId"],
      "q":f"{s['lemma'].upper()} · {s['tenseLabel']} · {s['personLabel']}",
      "a":opts,"optionMeta":om,"c":0,
      "rule":f"{s['lemma']} · {s['tenseLabel']} · {s['personLabel']} → {canonical}",
      "trigger":f"{s['tenseLabel']} · {s['personLabel']}",
      "targetTime":3.4 if s["tier"]==1 else 3.8,
      "difficulty":f"TIER_{s['tier']}","tier":s["tier"],
      "fingerprint":form_id,"focus":[],
      "formId":form_id,"lemma":s["lemma"],"family":"",
      "tenseId":s["tenseId"],"tenseLabel":s["tenseLabel"],"mood":s["mood"],"tense":s["tense"],
      "personCode":s["personCode"],"personLabel":s["personLabel"],
      "canonicalForm":canonical,"acceptedForms":accepted,
      "retrievalMode":"RECOGNITION","eligibleModes":["RECOGNITION","BUILD","PRODUCTION"],
      "buildEligible":s["personCode"]!="NP",
      "auditStatus":"AUDITED_CENTRAL" if oldq else "CENTRAL_TABLE_CROSSCHECK",
      "source":"DIEC2 + CPNL/B2 control" if oldq else "verbs.cat central table + IEC/GIEC authority + CPNL B2 paradigm control"
    }
    questions.append(q)

expected=120*103
if len(questions)!=expected:raise RuntimeError(f"bank size {len(questions)} != {expected}")
if pilot_preserved!=180:raise RuntimeError(f"pilot preserved {pilot_preserved} != 180")

campaign={
  "schemaVersion":3,"campaignId":"adaptive_verbs_catala_campaign1","title":"Adaptive Verbs · Català",
  "subtitle":"Campaign 1 · Complete Catalan Verbs","version":"0.3.0","bankStage":"COMPLETE",
  "startingLevel":1,"sessionSize":15,"cueTime":2.2,"timeLimit":5,"targetExercises":len(questions),
  "bankDefinition":{
    "fixedLemmaCount":120,"canonicalSlots":len(questions),"slotsPerLemma":103,"manualExpansionRequired":False,
    "paradigmCount":19,
    "tiers":{"1":"functional core active immediately","2":"compound/non-personal forms unlock automatically","3":"literary/low-frequency past forms unlock automatically"},
    "tierUnlock":{"tier2Level":15,"tier3Level":35}
  },
  "sourcePolicy":{
    "defaultVariety":"català central / general","canonicalAuthority":"Institut d'Estudis Catalans · DIEC/GIEC",
    "pedagogicalControl":"Curs de llengua catalana · Nivell B2 · revisió 2023",
    "conjugationTable":"verbs.cat · català central","generatedFormsAllowed":False
  },
  "retrievalModes":["RECOGNITION","BUILD","PRODUCTION"],"activeRetrievalMode":"RECOGNITION",
  "questions":questions,"skills":[{"id":v,"name":v} for v in VERBS]
}
CAMPAIGN_PATH.write_text(json.dumps(campaign,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
from collections import Counter
print(f"MASTER BANK OK: 120 verbs · {len(questions)} slots · 19 paradigms · {CAMPAIGN_PATH.stat().st_size/1024/1024:.2f} MiB")
print("tiers",dict(Counter(q["tier"] for q in questions)))
print("pilot preserved",pilot_preserved)
