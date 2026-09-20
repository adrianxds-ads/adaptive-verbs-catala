# Adaptive Verbs · Català

PWA gamificada i adaptativa derivada tècnicament d'Adaptive English, dedicada exclusivament al domini de formes verbals catalanes.

## Campaign 1
Una sola campanya longitudinal amb **banc mestre tancat des del principi**. L'aprenentatge progressa pel scheduler, els modes de recuperació i l'SRS; no cal anar afegint contingut manualment.

### Master bank v0.3.0
- 120 verbs fixos.
- 19 paradigmes.
- 12.360 slots canònics.
- 15 preguntes per nivell.
- Temporització en dues fases: 2,2 s per llegir la consigna amb respostes ocultes + 5,0 s de resposta mesurada.
- Tier 1 funcional actiu des del principi.
- Tier 2 s'activa automàticament al nivell 15.
- Tier 3 s'activa automàticament al nivell 35.
- Les 180 formes auditades del pilot es conserven exactament i el progrés existent no es reinicia.
- Recognition actiu; l'arquitectura continua preparada per Build i Production.
- AVG HITS /15, TARGET, Focus Time, Learning Curve, Coverage, Mastery i Automatic.
- Verb League + Tense League.
- Metadades d'error per forma i SRS longitudinal.
- Adrián Visual System conservat.

## Cobertura verbal
El banc combina verbs d'alta utilitat amb famílies morfològiques representatives: conjugacions regulars, irregulars, tercera conjugació pura/incoativa, verbs amb alternances d'arrel i formes ortogràficament sensibles.

## Paradigmes
Indicatiu: present, imperfet, perfet, plusquamperfet, passat simple, passat anterior, passat perifràstic, passat anterior perifràstic, futur i futur perfet.

Subjuntiu: present, imperfet, perfet i plusquamperfet.

També: condicional, condicional perfet, imperatiu, gerundi i participi.

## Fonts i control
- Referència normativa: IEC / GIEC.
- Control pedagògic: dossier B2 revisat segons normativa IEC.
- Extracció massiva: taules de conjugació catalana central de verbs.cat.
- Cap forma del banc es genera lliurement amb IA.
- Les variants acceptades es guarden com a variants i mai no es fan servir com a distractors.
- Les 180 formes originals actuen com a prova de regressió: si alguna canvia, el generador falla.

## Scheduling
Tot el contingut ja existeix dins Campaign 1. Els tiers només regulen quan el scheduler pot seleccionar una forma:
- Tier 1: nucli funcional i contrastiu.
- Tier 2: compostos i formes no personals.
- Tier 3: temps de baixa freqüència o més literaris.

Això evita tant la memorització d'un microbanc com l'exposició caòtica a 12.360 formes sense repetició suficient.

## Quality gate
- `python tools/audit_master.py` valida els 12.360 slots, IDs únics, metadades mínimes, quatre opcions úniques, variants acceptades i les 180 formes originals.
- `python tools/build_master_bank.py` reconstrueix el banc mestre des de les taules font i s'atura si detecta una regressió en el pilot auditat.
