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
| Nominalized act | Dokonał oceny; przeprowadzić weryfikację. | Is this a named procedure, or does a shorter verb keep the actor and act? |
| Purpose frame | W celu dokonania; celem przeprowadzenia. | Check the actor and any legally material purpose. |
| Date frame | Na dzień dzisiejszy; w dniu dzisiejszym. | Check quotations and document labels. |

Examples for context review:

- `Warto zauważyć, że API zwraca 204.` → `API zwraca 204.` only when
  the opener carries zero contrast or emphasis required by the surrounding text.
- `Anna może zapłacić 1 234,56 zł, jeśli Piotr podpisze umowę.` stays intact.
- `Dźwignia przenosi obciążenie.` stays intact. A literal mechanism is a fact.
- `„Warto podkreślić” to cytat.` stays intact.
- `Szanowni Państwo, proszę o podpis.` stays intact in a letter.
- `Może wystąpić błąd API.` stays intact. Modality describes uncertainty.
- `Algorytm układa terminy.` stays intact when the source shows no defect.
- `Przy rozsądnym nakładzie czasu` retains its time criterion. `Bez
  niepotrzebnych powtórek` changes that criterion.
- `Zapamiętaj:` can serve as a recap in teaching material. Changing the label
  to `Rola FSRS:` alone repairs no defect.
- `Technologia przesuwa granicę wykonalności, a człowiek zaczyna traktować nową granicę jak minimum.` stays intact without a demonstrated defect. `Większa liczba zadań` narrows its meaning and loses the actor.
- `Nie każda minuta spędzona w mediach społecznościowych jest stracona...` can introduce a substantive qualification. Its contrast alone supplies no finding.
- `czy ten czas wolno przeznaczyć na mniej pracy` keeps permission and scope. Replacing it with `można ... mniej obowiązków` changes both.

CLI: `python -B scripts/suggest.py tekst.md --language pl` emits candidate spans.
`python -B scripts/banned_phrase_scan.py tekst.md --language pl` audits phrases.
Offsets are Python character indices in the original text, rather than byte or
UTF-16 offsets. Neither command rewrites prose.

Lexical routing is a heuristic. Polish lexical cues can route short prose with
English API names. Shared words, English acronyms and currency alone supply no
Polish evidence. Ambiguous fragments and mixed-language quotations can require
an override. Polish voice training and stylometry await validation.
Numeric `PLN` and `zł` amounts retain exact surface protection on the English
route, including short fragments such as `3,5 PLN` and `-3,5 zl`.

## v0.3 matching and context limits

The catalog uses bounded phrase regexes. Supported inflections include
`odgrywa/odgrywają/odgrywał/odgrywała/odgrywały/odgrywali kluczową rolę`,
`kompleksowe podejście / kompleksowego podejścia / kompleksowym podejściem`,
the same adjective/noun cases for `przełomowe rozwiązanie`,
`zaadresować problem/problemy/kwestię/kwestie` and
`zaadresowania problemu/problemów/kwestii`. Standalone `kluczowa rola` is also
a candidate. Other inflections and paraphrases require whole-source review.

v0.3 adds closed forms of `dokonać/dokonał/dokonano` with `oceny/analizy/wyboru/przeglądu`, selected `przeprowadzić/wykonać` collocations, `w celu/celem dokonania/wykonania/przeprowadzenia`, two date frames, and `trzeba podkreślić/podkreślić należy/podkreślenia wymaga`. These are soft candidates. The [UW plain-language standard](https://www.uw.edu.pl/wp-content/uploads/2024/10/prosty-jezyk-%E2%80%93-standard.pdf) gives `dokonać oceny → ocenić` and `w celu złożenia → aby złożyć` as audience-sensitive examples. Neither example licenses a mechanical replacement. Preserve named acts, material purposes, attribution, modality and source voice. A legal or scientific context alone leaves the candidate for review; quotations and code stay masked. Literal `podkreślić należy tekst/wyraz/fragment` is suppressed.

A matching view maps only Polish letters to ASCII, one character to one.
Case-insensitive matching accepts `Warto zauwazyc` and `ODGRYWAL KLUCZOWA ROLE`.
It returns original surfaces and offsets, including beside English names.
Quotes and code retain masking. Scripts neither restore accents nor normalize
Unicode; decomposed combining accents remain outside this matching rule.

Local protections cover a line-opening `Szanowni Państwo` followed by a comma,
exclamation mark or line end; `niniejszym informujemy o` followed by
`odstąpieniu od umowy`, `rozwiązaniu umowy` or `wypowiedzeniu umowy`;
and literal `należy zaznaczyć pole wyboru/checkbox`. Role candidates are protected
when immediately followed by `polega na` (optionally after
`administratora/walidatora/serwera`) or a colon introducing
`sprawdza/weryfikuje/odrzuca/blokuje/przekazuje`. ASCII spellings share these rules.
`Dedykowany serwer` supplies no candidate by itself.

These cues protect only their span. A letter, API term or `umowa` leaves other
matches active. For example, `Szanowni Państwo, warto zauważyć, że API działa.`
retains the framing candidate. `API odgrywa kluczową rolę w sukcesie firmy.`
stays a candidate; a mechanism expressed outside the listed definition forms
also stays for agent judgment. Legal obligations, modality, passive voice,
nominalizations and dashes alone supply no defect. Quoted boilerplate stays
masked unless quoted scanning is requested. This is candidate detection,
rather than morphology or semantic understanding; Polish quality is unmeasured.

## Preservation and completed review

Carry `--language pl` through extraction, validation and suggestion checks for
short or ambiguous sources. Validation also supplements cached constraints with
Polish constraints, including exact numeric surfaces and adjacent quantity
qualifiers and units. Quantity coverage uses a unit list; review the remaining
wording against the source.
ASCII cues use the same checks for negation, modality, conditions, scope and
attribution. Dates such as `12 pazdziernika 2026` and amounts such as `3,5 zl`
retain their original surfaces. These checks warn about cue changes and block
lost extracted quantities/dates; they still require claim-by-claim review.

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
