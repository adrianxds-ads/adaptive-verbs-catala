from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
app = root / "app.js"
text = app.read_text(encoding="utf-8")

repls = {
    'const APP_VERSION = "0.1.0";': 'const APP_VERSION = "0.1.1";',
    'const keysUnlocked=Math.min(25,Array.isArray(state.keyring)?state.keyring.length:0);': 'const keysUnlocked=Math.min(baseKeyCount(),Array.isArray(state.keyring)?state.keyring.length:0);',
    'keys:st.keysUnlocked>=25': 'keys:st.keysUnlocked>=baseKeyCount()',
    'const stage=ready?"Campaign 2 gate achieved":score>=.72?"Late consolidation":score>=.55?"Building graduation evidence":"Building foundation";': 'const stage=ready?"Pilot evidence complete":score>=.72?"Late consolidation":score>=.55?"Building retention evidence":"Building foundation";',
    'if(!g.gates.keys)blockers.push(\`\${25-st.keysUnlocked} more base Keys to unlock\`);': 'if(!g.gates.keys)blockers.push(\`\${Math.max(0,baseKeyCount()-st.keysUnlocked)} more base Keys to unlock\`);',
}
for old, new in repls.items():
    if old not in text:
        raise SystemExit(f"missing app replacement: {old[:70]}")
    text = text.replace(old, new)

text = re.sub(
    r'function campaign2Brief\(\)\{.*?\n\}',
    '''function campaign2Brief(){
  const r=campaign2Readiness(),st=overallStats();
  return \`Adaptive Verbs · Català · Campaign 1 diagnostic. Use my exported GLOBAL JSON as the primary longitudinal source. This is one continuous campaign: do not create Campaign 2. Current pilot: \${BANK.length} canonical forms, 15 questions per level, fixed 6-second clock. Current evidence: readiness \${pct(r.score)}%, coverage \${pct(st.coverage)}%, mastery \${pct(st.mastery)}%, weakest verb \${pct(st.minSkill)}%, review retention \${pct(r.graduation.retentionAccuracy)}% across \${r.graduation.reviewCount} spaced-review answers, automatic \${pct(st.auto)}%, 8-level stability \${pct(r.graduation.stableAccuracy)}%, real evidence span \${r.graduation.spanDays.toFixed(1)} days, Key Diary \${st.keysUnlocked}/\${baseKeyCount()}. Analyse verb, tense/mood, person, stem, ending and orthographic errors. The pilot bank is not campaign completion unless bankStage is COMPLETE.\`;
}''',
    text, count=1, flags=re.S
)

text = re.sub(
    r'const RELEASE_NOTES=\[.*?\];\nfunction renderReleaseInfo',
    'const RELEASE_NOTES=["v0.1.1 audits all 180 pilot forms against the central paradigms used by DIEC2/IEC and the B2 model tables.","English-only Error Coach material has been replaced by Catalan verb coaching for the 10 pilot verbs.","Key Journey graduation now scales to the active verb bank instead of the inherited 25-key English gate.","Visible dashboard labels and release metadata now use Adaptive Verbs terminology."];\nfunction renderReleaseInfo',
    text, count=1, flags=re.S
)
text = text.replace('\"v0.1.0 · Pilot: 180 canonical forms · 10 verbs × 3 paradigms × 6 persons\"','\"v0.1.1 · Pilot audited: 180 canonical forms · 10 verbs × 3 paradigms × 6 persons\"')
text = text.replace('Campaign 2 handoff copied. Export your progress too and send both to ChatGPT.','Campaign 1 diagnostic copied. Export your progress too and send both to ChatGPT.')
app.write_text(text, encoding="utf-8")

index = root / "index.html"
html = index.read_text(encoding="utf-8")
html = html.replace('<span>AE rating</span>','<span>Verb control</span>')
html = html.replace('<b id="startMastered">0/25</b><span>Keys mastered</span>','<b id="startMastered">0/10</b><span>Verbs mastered</span>')
html = html.replace('<span>Repeated phrases</span>','<span>Repeated forms</span>')
html = html.replace('<div class="resulttitle"><div class="kicker">DASHBOARD · v3.0</div><h1>Statistics</h1><p>Your full learning snapshot before the next level.</p></div>','<div class="resulttitle"><div class="kicker">DASHBOARD · v0.1.1</div><h1>Statistics</h1><p>Longitudinal snapshot before the next level.</p></div>')
html = html.replace('Graphs · progress · keys','Graphs · progress · verb keys')
html = html.replace('What the algorithm thinks you should review right now.','What the algorithm thinks you should review in Catalan verbs right now.')
html = html.replace('?v=3.18','?v=0.1.1')
index.write_text(html, encoding="utf-8")

manifest = root / "manifest.webmanifest"
m = manifest.read_text(encoding="utf-8")
manifest.write_text(m.replace("Adaptive Verbs · Català · Campaign 1","Adaptive Verbs · Català · Campaign 1"), encoding="utf-8")

sw = root / "service-worker.js"
s = sw.read_text(encoding="utf-8").replace("avc-campaign1-v0.1.0","avc-campaign1-v0.1.1")
sw.write_text(s, encoding="utf-8")
