# NoCap 0.2

NoCap extends Unslop with Polish phrase audit and agent-reviewed rewrite.
English commands, phrase rules, presets and voice tools remain available.
Version 0.2 adds bounded phrase inflections, ASCII Polish matching and local
protections for correspondence, instructions, role definitions and legal notices.
Polish prose can contain English API terms. Matches retain the source spelling
and character offsets. These changes carry no measured Polish quality claim.

## Install and use

Copy this folder into your agent's skills directory as `nocap`, or load
`SKILL.md` from this checkout. Python 3.10+ runs the scripts; dependencies use
the standard library. Keep `scripts`, `references` and `presets` beside the skill.

- `/nocap rewrite tekst.md` or "Usuń ślady AI z tego tekstu".
- `/nocap cleanup --report tekst.md` or "Wskaż problemy, bez zmian".
- `/nocap teach samples/` and `/nocap mimic ...` retain English voice workflows.
- Presets: `crisp`, `warm`, `expert`, `story`. Legacy `/unslop` command examples
  in inherited references describe the same command names.

```sh
python -B scripts/banned_phrase_scan.py tekst.md --language pl
python -B scripts/suggest.py tekst.md --language pl
python -B scripts/validate_preservation.py original.txt transformed.txt --language pl
python -B scripts/nocap_smoke.py
```

Use `--language en` or `--language pl` when routing needs an override. Defaults
use lexical routing and English for ambiguous ASCII input. Other languages
receive a decline where detected. Routing is a heuristic, rather than a language
identifier with validated recall. Phrase scans return exit 1 for candidate hits.

Polish matches require context review. Scripts emit candidates, never permission
to rewrite. The agent preserves language, register, facts, roles and attribution;
uncertainty returns the source. Preservation regexes check extracted surfaces,
rather than proving meaning. A changed Polish draft requires agent review. Follow the
[completion flow](references/polish.md#preservation-and-completed-review), then run
`check_suggestions.py suggestions.json --language pl --reviewed`. Protected
candidates may remain; hard preservation failures still block acceptance.
Polish Flesch, structure/silhouette gates, rubric scores and voice training or
scoring are unavailable in v0.2. English keeps its existing tooling.

## Provenance and licensing

Original Unslop: Clayton Kim (`claytonkim`),
[theclaymethod/unslop](https://github.com/theclaymethod/unslop),
SHA `17ed39c9d0b522f44190ff0c6233867eadee192a`.
Root source was bootstrapped from tracked files at that commit.
`upstream/unslop` is an ignored local comparison checkout. `research/` contains
separate user material and supplies no copied Polish rules or repository license.

Upstream declares MIT in its skill frontmatter and README. Those declarations
and author attribution are retained. The source snapshot contains no standalone
LICENSE file. NoCap adds no repository license declaration.

The [upstream README](docs/UPSTREAM-README.md), `docs/` and `references/` retain
English technical documentation. [AGENTS.md](AGENTS.md) defines development checks;
[the core contract](references/core-contract.md) defines editing behavior.
