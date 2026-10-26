# Polish audit reference

Behavior and validation: [core-contract.md](core-contract.md).
Candidate catalog: `POLISH_PHRASES` in `scripts/banned_phrase_scan.py`.
All candidates use soft severity; replacement fields start as null.

| Candidate family | Example | Context to inspect |
|---|---|---|
| Empty framing | Warto zauważyć, że API zwraca 204. | Does the opener add a distinction? |
| Emphasis | Odgrywa kluczową rolę. | Does the source define the role? |
| Jargon / calque | Wykorzystać synergię; zaadresować problem. | Check domain meaning; a synergy calculation is valid. |
| Chatbot residue | Jako model językowy; oto poprawiona wersja. | A description of a model or a quoted response is valid. |
| Praise | Przełomowe rozwiązanie; kompleksowe podejście. | Check the stated change, mechanism or evidence. |
| Formality | Niniejszym informujemy; Szanowni Państwo. | A notice, letter or legal register can require these forms. |

Examples for context review:

- `Warto zauważyć, że API zwraca 204.` → `API zwraca 204.` only when
  the opener carries zero contrast or emphasis required by the surrounding text.
- `Anna może zapłacić 1 234,56 zł, jeśli Piotr podpisze umowę.` stays intact.
- `Dźwignia przenosi obciążenie.` stays intact. A literal mechanism is a fact.
- `„Warto podkreślić” to cytat.` stays intact.
- `Szanowni Państwo, proszę o podpis.` stays intact in a letter.
- `Może wystąpić błąd API.` stays intact. Modality describes uncertainty.

CLI: `python -B scripts/suggest.py tekst.md --language pl` emits candidate spans.
`python -B scripts/banned_phrase_scan.py tekst.md --language pl` audits phrases.
Offsets are Python character indices in the original text, rather than byte or
UTF-16 offsets. Neither command rewrites prose.

Lexical routing is a heuristic. Short fragments and mixed-language quotations
can require an override. The catalog omits inflectional and paraphrase coverage;
read the whole source. Polish voice training and stylometry await validation.

## Preservation and completed review

Carry `--language pl` through extraction, validation and suggestion checks for
short or ambiguous sources. Validation also supplements cached constraints with
Polish constraints, including exact numeric surfaces and adjacent quantity
qualifiers and units. Quantity coverage uses a unit list; review the remaining
wording against the source.

```sh
python -B scripts/extract_constraints.py original.txt --language pl
python -B scripts/validate_preservation.py original.txt transformed.txt --language pl
python -B scripts/check_suggestions.py suggestions.json --language pl --reviewed
```

Before `--reviewed`, inspect every candidate in context. Record each confirmed
defect or protected use with its reason in the agent report. Supply a replacement
for every confirmed defect; leave a protected suggestion's replacement null or
omit that suggestion. Read all changed claims against the source, including
roles, owners, attribution, negation, modality, conditions, scope and register.
On uncertainty restore the source span. Then pass `--reviewed` to acknowledge
that review. The flag acknowledges the whole resulting document, including
candidates introduced by replacements. A protected formal greeting can remain.

The acknowledgment clears the Polish candidate/meaning-review gate. Span,
overlap and hard preservation failures still block acceptance. English scanner
gates stay in force. CLI JSON reports `review_acknowledged` and preservation
warnings. Review each warning; regex checks supply no guarantee of meaning.
Preservation `--strict` continues to fail on warnings, including the reminder
attached to every Polish edit. Use the default preservation check plus the
reviewed suggestion check for the Polish completion flow.

Python callers use `extract_constraints(text, language="pl")`,
`validate_preservation(source, output, constraints, language="pl")` and
`check(document, suggestions, language="pl", reviewed=True)`. Existing positional
arguments keep their meaning. Suggestion checks inherit the JSON `language`
field unless the CLI selects a language. Pass the override again for separate
extraction and validation commands.
