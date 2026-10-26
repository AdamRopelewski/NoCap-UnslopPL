# Development instructions

NoCap extends Unslop. Preserve English commands, presets, phrase rules and CLI
APIs. Keep behavior in `references/core-contract.md`; load `references/polish.md`
only for Polish work. Use Serena for structural code exploration. Read callers
before changing shared helpers.

Keep `upstream/unslop` and `research/` untouched. Preserve user edits and the Git index. Leave commits and staging to the
user. Preserve attribution and license declarations; add no inferred license.

For v0.1, use one assert-based smoke check and fixed English CLI comparisons
against upstream when the comparison checkout exists; report skipped comparisons
when absent. Compile/import touched scripts without bytecode artifacts.
Run touched CLI help and `git diff --check`. Verify upstream SHA/status and the
staged research PDF. Skip model calls, benchmarks, eval expansion and broad
suites unless the user authorizes them. Upstream eval procedures remain in
`references/maintenance.md` for work with that scope. Keep benchmark assertions
and fixtures intact.

A phrase match is a candidate. Add a true-match and protection case to the smoke
check when extending Polish rules. Check original offsets, quotes/code, routing
and preservation. Guard literal/domain uses. English metrics supply no Polish
hard gates. New dependencies and packaging require task scope.

Before editing agent instructions, read the `writing-for-agents` skill and its
`SKILL-MECHANICS.md` from the installed skill catalog.
