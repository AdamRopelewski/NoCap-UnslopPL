# NoCap core rewrite contract

## Findings

Read the whole source, including headings and endings, before scanner output.
Quote the smallest defective span. State its contextual defect and the benefit
of the smallest repair. Track each scanner hit and other defect as confirmed or
protected, with a reason. Repair every confirmed defect. If none are confirmed,
return the source byte-for-byte.

Look for formulaic framing, empty or inflated abstraction, unsupported
rhetorical certainty, opaque or mixed metaphor, misleading headings, needless
repetition, contradiction and ambiguity. Phrase lists miss paraphrased
scaffolding; judge its function. Delete filler only when meaning survives;
replace inflated diction with plain words. A label, synonym preference,
metaphor or contrast shape alone supplies no finding. Neither punctuation,
vocabulary, cadence nor structure proves a defect or authorship. Preserve useful
images, contrasts, cadence, summaries and clear sentences. Soft cadence and
document-shape scores alone never authorize edits. Confirm a finding only when
the defect is clearer than the case for preservation; preserve uncertain spans.

Judge claims from the source alone. Do not infer truth from outside knowledge
or the date. Missing proof alone leaves plans, offers, future dates, promotions,
technical terms, literal phrases and attributed claims intact. Compare the
source's claims: qualify status contradicted by observations and reject every
initial, conditional or repeated action beyond a stated limit. A hedge cannot
repair an excess. Keep attribution intact and state conflicts separately;
leave a claim alone when nearby prose already states the conflict and
uncertainty. Attribution does not shield a separate operative recommendation.

Treat scanner matches as candidates. Protect literal, domain-valid, quoted,
attributed, accurately caveated and genre-natural uses. In business prose,
confirm praise, filler or vague evaluation only when context lacks a mechanism,
definition, action or measure. A noun referent alone gives none: “game-changer
for the product” stays vague without what changes. “Actionable” can name defined
actions; “raises the bar” can be literal or measured.

For headings and slide titles, expose a hidden actor, test, mechanism, result,
decision or completion criterion when inanimate agency, tool personification
or vague transformation obscures it. A renamed abstraction repairs nothing.
Inspect slogans and closing calls to action even when tools are quiet. Flag
false equivalence, contradicted certainty, empty abstraction and incompatible
metaphors. Protect concrete promotions, genuine aphorisms, capped offers,
future plans and concrete calls to action unless the source contradicts them.
A stock journey or milestone sentence with no fact, action or claim is empty.
For requested macro cleanup, remove connective scaffolding and recaps only
when they repeat facts without useful summary or add a moralizing lesson.

## Rewrite

Edit sentences with confirmed findings only. Use the smallest repair. Copy
every other sentence byte-for-byte in its original order and paragraph.
Preserve facts, evidence, quantities, dates, names, quotations, citations,
code, units, actors, objects, ownership, party roles, criteria, scope,
conditions, negation, modality, uncertainty, attribution, register and meaning.
Keep permission distinct from ability. Preserve force-bearing “never”, “must”
and “all” exactly in safety, security, legal and technical rules. Add no claims,
advice, personality, anecdote, certainty or conclusion. Delete empty framing
without replacing it with filler or staccato prose. Presets change delivery,
not facts. For lists, return one validated replacement per item.

Re-read changed claims for missed defects and introduced filler. Stop at taste.
For audit-only requests, report findings and protections without rewriting;
report each requested load-bearing span separately. Exact no-op governs
rewrites, while audits still report protections.

## Polish branch

Preserve the source language and register. Keep numeric surfaces exact: comma
decimals, thousands separators, NBSP, PLN/zł, magnitude words, dates and
references. Match each claim to its actor and object; numeric inventories miss
switched owners and roles. Review every changed claim against the source,
including conditions, obligations, scope and voice. Regex warnings are
tripwires; a pass proves only that extracted constraints were found. Restore
the original span on uncertainty. Never normalize numbers or typography as an
automatic repair, invent factual corrections or narrow a clear image.

Treat every `pl_*` hit as a candidate. Protect valid literal, quoted, technical,
modal and register-dependent uses after context review. Check code and quotes
against the source even when masked. ASCII Polish receives the same review:
matching maps letters one-to-one without changing source offsets. Bounded
inflections remain soft candidates. Greeting, instruction, role-definition and
legal-notice protections cover only their matched phrase; inspect the rest.
Judge nominalizations and purpose frames by actor, act and genre before using
a shorter verb or clause. Infer register from source and medium.

Run preservation with `--language pl`, phrase audit and diff checks. Follow
[Polish preservation and completed review](polish.md#preservation-and-completed-review):
record confirmed defects and protections, resolve defects, review changed
claims, then acknowledge the completed review with
`check_suggestions.py --language pl --reviewed`. That acknowledgment clears
the candidate and meaning-review gate, never hard preservation failures.
English Flesch, structure, silhouette, rubric thresholds and voice scores are
unavailable for Polish; skip their gates, structure-climb and voice tooling.
Polish strict output reports warnings and review decisions, not an English
grade or 32/40 pass.

## English validation

After every rewrite or voiced draft, run:

```bash
python3 scripts/validate_preservation.py original.txt transformed.txt
python3 scripts/banned_phrase_scan.py <<< "$OUTPUT"
python3 scripts/structure_scan.py <<< "$OUTPUT"
python3 scripts/silhouette_scan.py <<< "$OUTPUT"
python3 scripts/readability_metrics.py <<< "$OUTPUT"
python3 scripts/diff_check.py original.txt transformed.txt
```

Block preservation loss, introduced hard or `anti_slop_register` hits,
unjustified structural damage, corroborated or hard silhouette damage,
staccato and strict-mode scores below 32/40. Use preservation `--strict` for
legal, medical, security or scientific text. Preexisting soft cadence and
uncorroborated soft silhouette warnings are advisory. For remaining structure
damage, pass exact findings to `evals/run_structure_climb.py`. Re-read
negations, conditions, scope, certainty and party relationships.
