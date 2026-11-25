#!/usr/bin/env node
/**
 * The rules of the Credits Importer as one list (Z-RULESINDEX, 3.219.0): the register of the script (S, D, T, X), the role rules (R),
 * the questions (Q) and the wording rules (W) of the mapping file – an id, whether it is off by default, its note, where it is.
 * The owner keeps the list beside the project's notes (regeln-index.md, its headings in German) and looks there before proposing a rule;
 * core check K-26 compares it with the script.
 *
 * Usage: node tools/rules_index.js <folder of the script> <out.md>
 *        node tools/rules_index.js <folder> <out.md> --check <existing.md>   exit code 1 when the existing list is not the one of the code
 */
const fs = require('fs');
const dir = process.argv[2] || '.', out = process.argv[3];
const checkAt = process.argv.indexOf('--check');
const against = checkAt > 0 ? process.argv[checkAt + 1] : null;
const src = fs.readFileSync(`${dir}/mb-vibecode-credits-importer.user.js`, 'utf8');
const map = JSON.parse(fs.readFileSync(`${dir}/mb-vibecode-credits-importer-mapping.json`, 'utf8'));
const ver = (src.match(/@version\s+(\S+)/) || [])[1];
const offRaw = map.DEFAULT_OFF_RULES || []; const off = new Set(Array.isArray(offRaw) ? offRaw : (offRaw.$set || []));
const reg = [];
const L = src.split('\n');
for (let i = 0; i < L.length; i++) {
  if (!/^    \{ id: '[A-Z]\d+',/.test(L[i])) continue;
  let s = L[i];
  for (let j = i; !/\},?\s*$/.test(s.trim()) && j < i + 30; ) s += '\n' + L[++j];
  try { reg.push(eval(`(${s.trim().replace(/,$/, '')})`)); } catch (e) {
    const id = s.match(/id: '([A-Z]\d+)'/)[1], note = (s.match(/note: '((?:[^'\\]|\\.)*)'/) || [])[1];
    const f = (k) => (s.match(new RegExp(`${k}: '((?:[^'\\\\]|\\\\.)*)'`)) || [])[1];
    reg.push({ id, note: note ? note.replace(/\\'/g, "'") : '', name: f('name'), kind: f('kind'), perms: f('perms'), since: f('since') }); // (a pattern of the date table: its note is in the register)
  }
}
// the connections (X): a site, a source or a service – what it is, its hosts and what the script needs for it
for (const r of reg) if (r.id[0] === 'X' && !r.note && r.kind) r.note = `${r.kind}: ${r.name || '(its name in the texts)'} – ${(r.hosts || []).join(', ')} – ${r.perms || ''}${r.since ? ` (since ${r.since})` : ''}`;
{
  const by = new Map();
  for (const r of reg) { const o = by.get(r.id); if (!o || String(r.note || '').length > String(o.note || '').length) by.set(r.id, { ...o, ...r, where: r.where || (o && o.where), note: r.note || (o && o.note) }); }
  reg.length = 0; reg.push(...[...by.values()].filter((r) => r.note));
  const none = [...by.values()].filter((r) => !r.note).map((r) => r.id);
  if (none.length) console.error('without a note:', none.join(', '));
}
const clean = (s) => String(s || '').replace(/\s+/g, ' ').trim();
const groups = { S: 'S – Regeln (Lesen, Zuordnen, Oberfläche)', D: 'D – Datumsregeln', T: 'T – Textregeln', X: 'X – Verbindungen (Seiten, Quellen, Dienste)' };
let md = `# Regel-Übersicht – MB x Vibecode: Credits Importer ${ver}\n\nErzeugt aus dem Skript (Regelregister) und der Mapping-Datei (R-Regeln, Rückfragen Q). Vor jedem Vorschlag hier nach Stichwörtern suchen; die Regel-ID nennen. „aus“ = standardmäßig ausgeschaltet.\n\n`;
for (const p of Object.keys(groups)) {
  const rs = reg.filter((r) => r.id[0] === p);
  md += `## ${groups[p]} (${rs.length})\n\n`;
  for (const r of rs) md += `- **${r.id}**${off.has(r.id) ? ' (aus)' : ''}: ${clean(r.note)}${r.where ? ` – _${clean(r.where)}_` : ''}\n`;
  md += '\n';
}
const rr = map.ROLE_RULE_DATA || [];
md += `## R – Rollen-Regeln der Mapping-Datei (${rr.length})\n\n`;
for (const r of rr) md += `- **${r.id}**${off.has(r.id) ? ' (aus)' : ''}: \`${r.re && r.re.$re ? r.re.$re : ''}\` → ${(r.types || []).join(', ') || r.kind}${r.level ? ` (${r.level})` : ''}${r.note ? ` – ${clean(r.note)}` : ''}\n`;
const qs = [...(map.QUESTION_RULES || []), ...(map.TYPE_QUESTIONS || [])];
md += `\n## Q – Rückfragen (${qs.length})\n\n`;
for (const q of qs) md += `- **${q.id}** „${q.base}“${q.rule ? ` (${q.rule})` : ''}: ${clean(q.note)} – Antworten: ${(q.options || []).map((o) => o.label || o.type).join(' · ')}\n`;
const wr = map.WORDING_RULES || [];
md += `\n## W – Formulierungs-Regeln (${wr.length})\n\n`;
for (const w of wr) md += `- **${w.id}**: ${clean(w.note)}\n`;
if (out) fs.writeFileSync(out, md);
if (against) {
  const old = fs.readFileSync(against, 'utf8');
  if (old !== md) {
    const a = old.split('\n'), b = md.split('\n');
    const gone = a.filter((x) => !b.includes(x)).slice(0, 10), added = b.filter((x) => !a.includes(x)).slice(0, 10);
    console.log('differs from the code:\n- ' + gone.join('\n- ') + '\n+ ' + added.join('\n+ '));
    process.exitCode = 1;
  } else console.log('same as the code');
}
console.log(`${reg.length} + ${rr.length} + ${qs.length} + ${wr.length} entries, ${md.length} characters`);
