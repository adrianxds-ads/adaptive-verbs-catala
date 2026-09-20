# Adaptive Verbs · Català

PWA gamificada i adaptativa derivada tècnicament d'Adaptive English, dedicada exclusivament al domini de formes verbals catalanes.

## Campaign 1
Una sola campanya longitudinal. El pilot NO és el final: és el primer banc activat.

### Pilot v0.2.0
- Jerarquia visual reforçada: verb → temps/mode → persona.
- Temporització en dues fases: 2,2 s de lectura de la consigna amb respostes ocultes + 5,0 s de resposta mesurada.
- 10 verbs: parlar, perdre, dormir, servir, anar, fer, tenir, poder, voler, veure.
- 3 paradigmes: present d'indicatiu, present de subjuntiu, imperfet de subjuntiu.
- 6 persones = 180 formes canòniques.
- 15 preguntes per nivell.
- Recognition actiu; Build i Production són la següent expansió pedagògica, no el final del pilot.
- AVG HITS /15, TARGET, Focus Time, Learning Curve, Coverage, Mastery i Automatic.
- Verb League + Tense League.
- Metadades d'error per forma i SRS longitudinal.
- Adrián Visual System conservat.

## Font lingüística
Les formes no es generen lliurement amb IA. El banc pilot s'ha construït amb font normativa IEC i control pedagògic del dossier B2 revisat segons normativa IEC.

## Regla de campanya
Campaign 1 només podrà marcar-se COMPLETE quan bankStage sigui COMPLETE. Cobrir el pilot no finalitza la campanya.

## Quality gate
- `python tools/audit_pilot.py` validates all 180 canonical pilot forms, IDs, four-option uniqueness and audit metadata before release.
