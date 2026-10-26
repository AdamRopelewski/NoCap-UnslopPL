#!/usr/bin/env python3
"""Offline NoCap checks. Run with python -B scripts/nocap_smoke.py."""
from pathlib import Path
import subprocess
import sys

from _lang import detect_language
from banned_phrase_scan import POLISH_PHRASES, mask_ignored_spans, scan_for_violations
from extract_constraints import extract_constraints
from check_suggestions import check as check_suggestions
from readability_metrics import calculate_metrics
from structure_scan import scan
from silhouette_scan import scan as silhouette
from suggest import build_suggestions
from validate_preservation import validate_preservation
from voice_profile import feature_bundle

checks = 0


def check(value):
    global checks
    assert value
    checks += 1


for text, language in [
    ("Warto zauważyć.", "pl"), ("Nie działa.", "pl"),
    ("Może wystąpić błąd API request timeout w SDK.", "pl"),
    ("Ten endpoint zwraca status code in JSON.", "pl"),
    ("This is the API response.", "en"), ("Deploy cache.", "en"),
    ("Bonjour, ceci est une réponse avec des exemples pour vous.", "unknown"),
    ("Hola gracias.", "unknown"), ("Привет это текст.", "unknown"),
]:
    check(detect_language(text) == language)
for headline in ["language model", "Data model", "Model selection", "Amounts in PLN", "The invoice is 500 PLN."]:
    check(detect_language(headline) == "en")
for phrase in POLISH_PHRASES:
    check(bool(scan_for_violations(phrase)))
check(detect_language("API", "pl") == "pl")
check(detect_language("Nie działa.", "en") == "en")
check(bool(scan_for_violations("Warto zauważyć, że API działa.")))
check(scan_for_violations("Dźwignia przenosi obciążenie. Może wystąpić błąd API.") == [])
text = 'Łódź.\nŻółw: Warto podkreślić, że API działa.'
suggestion = build_suggestions(text)[0]
span = suggestion["span"]
check(text[span["start"]:span["end"]] == "Warto podkreślić")
check(span["start"] == text.index("Warto"))
for protected in ['„Warto podkreślić”', '«Warto podkreślić»',
                  '`Warto podkreślić`', '```pl\nWarto podkreślić\n```',
                  '~~~pl\nWarto podkreślić\n~~~', '    Warto podkreślić',
                  '> Warto podkreślić', '``Warto podkreślić``']:
    check(scan_for_violations(protected, language="pl") == [])
    check(len(mask_ignored_spans(protected)) == len(protected))
check(bool(scan_for_violations('„Warto podkreślić”', include_quoted=True, language="pl")))
check(scan_for_violations('```\nWarto podkreślić', language="pl") == [])
check(scan_for_violations('```Warto podkreślić', language="pl") == [])
source = "Anna może zapłacić tylko 1 234,56 zł i 3,5 mln zł 12 marca 2026, jeśli Piotr nie podpisze umowy (art. 5)."
check(validate_preservation(source, source)["passed"])
check(validate_preservation(source, source)["warnings"] == [])
constraints = extract_constraints(source)
for value in ["1 234,56 zł", "3,5 mln zł", "12 marca 2026", "art. 5"]:
    check(any(c["value"] == value for c in constraints))
for old, new in [("1 234,56 zł", "1 234,57 zł"), ("3,5 mln zł", "3,5 mld zł"),
                 ("12 marca 2026", "13 marca 2026"), ("art. 5", "art. 6")]:
    check(not validate_preservation(source, source.replace(old, new))["passed"])
for old, new, marker in [("nie ", "", "negation"), ("może", "musi", "modality"),
                          ("jeśli", "ponieważ", "condition"), ("tylko ", "", "scope")]:
    result = validate_preservation(source, source.replace(old, new))
    check(any(marker in w for w in result["warnings"]))
iso = "Anna musi podpisać umowę 2026-03-12."
check(not validate_preservation(iso, iso.replace("03-12", "03-13"))["passed"])
for space in ["\u00a0", "\u202f"]:
    text = "Kwota wynosi 1" + space + "234,56 PLN."
    check(validate_preservation(text, text)["passed"])
    check(not validate_preservation(text, text.replace("234,56", "234,57"))["passed"])
roles = "Anna przekazuje Piotrowi 500 zł."
check(any("roles" in w for w in validate_preservation(roles, "Piotr przekazuje Annie 500 zł.")["warnings"]))
for result in [calculate_metrics(source), scan(source), silhouette(source, {})]:
    check(result["available"] is False and result["flags"] == [])
try:
    feature_bundle(source)
except ValueError:
    check(True)
else:
    check(False)
check(build_suggestions("Może wystąpić błąd API.") == [])
suggestions = build_suggestions("Warto zauważyć, że API działa.")
suggestions[0]["suggested_replacement"] = ""
check(any(f["gate"] == "agent-review" for f in check_suggestions("Warto zauważyć, że API działa.", suggestions)))

# Routing and explicit source language must reach every preservation step.
currency = "Klient otrzyma 3,5 PLN."
check(detect_language(currency) == "pl")
check(not validate_preservation(currency, currency.replace("3,5", "3,6"))["passed"])
for sign in ["-", "−"]:
    signed = f"Kwota wynosi {sign}3,5 PLN."
    check(validate_preservation(signed, signed, language="pl")["passed"])
    check(not validate_preservation(signed, signed.replace(sign, ""), language="pl")["passed"])
    check(not validate_preservation("Koszt: 3,5.", f"Koszt: {sign}3,5.", language="pl")["passed"])
short = "Koszt: 3,5."
check(any(c["value"] == "3,5" for c in extract_constraints(short, "pl")))
check(not validate_preservation(short, "Koszt: 3,6.", language="pl")["passed"])
check(not validate_preservation(short, "Koszt: 3,6.", [], language="pl")["passed"])
check(any("roles" in w for w in validate_preservation(short, "Cena: 3,5.", language="pl")["warnings"]))
for original, changed in [
    ("Limit wynosi 5 kg i 10 m.", "Limit wynosi 5 m i 10 kg."),
    ("Limit wynosi ponad 5 kg.", "Limit wynosi mniej niż 5 kg."),
    ("Limit wynosi 5 kg.", "Limit wynosi 15 kg."),
    ("Limit wynosi 5 kg.", "Limit wynosi ponad 5 kg."),
    ("Limit wynosi ponad 5 kg.", "Limit wynosi 5 kg."),
    ("Limit wynosi 3,5 kg.", "Limit wynosi 13,5 kg."),
]:
    check(validate_preservation(original, original)["passed"])
    check(not validate_preservation(original, changed)["passed"])
greeting = "Szanowni Państwo, proszę o podpis."
check(check_suggestions(greeting, [], reviewed=True) == [])
check(check_suggestions(greeting, build_suggestions(greeting), reviewed=True) == [])
cleanup = "Warto zauważyć, że API działa."
span_text = "Warto zauważyć, że "
edits = [{"span": {"start": 0, "end": len(span_text), "text": span_text},
          "suggested_replacement": ""}]
check(check_suggestions(cleanup, edits, reviewed=True) == [])
check(any(f["gate"] == "agent-review" for f in check_suggestions(cleanup, edits)))
for original, old, new in [(short, "3,5", "3,6"), (currency, "3,5", "3,6"),
                            ("Limit wynosi 5 kg i 10 m.", "5 kg i 10 m", "5 m i 10 kg")]:
    start = original.index(old)
    edits = [{"span": {"start": start, "end": start + len(old), "text": old},
              "suggested_replacement": new}]
    check(any(f["gate"] == "accept-all" for f in
              check_suggestions(original, edits, language="pl", reviewed=True)))

root = Path(__file__).resolve().parents[1]
upstream = root / "upstream" / "unslop"
comparisons = 0
# Compare stdout, stderr and exit status without writing inputs or bytecode.
if (upstream / "scripts").is_dir():
    for script, text in [
        ("banned_phrase_scan.py", "In today's fast-paced world, we leverage synergy to unlock potential."),
        ("banned_phrase_scan.py", "Leverage synergy. Unlock potential. Foster innovation. Seamless integration. Robust solutions. Comprehensive capabilities. Enhance performance. Streamline workflows. Empower teams."),
        ("banned_phrase_scan.py", 'The lever raises the bar. "Unlock potential" is a quote.'),
        ("suggest.py", "It is important to note that the API returns 204."),
        ("extract_constraints.py", "The API costs $12.50 for 2,500 users on January 12, 2026."),
        ("readability_metrics.py", "The API returns a status code. We use the code to decide whether to retry."),
        ("structure_scan.py", "The API returns a status code. We use the code to decide whether to retry."),
        ("silhouette_scan.py", "The API returns a status code. We use the code to decide whether to retry."),
    ]:
        results = [subprocess.run([sys.executable, "-B", str(base / "scripts" / script)],
                                 input=text.encode("utf-8"), capture_output=True) for base in [root, upstream]]
        check((results[0].returncode, results[0].stdout, results[0].stderr) ==
              (results[1].returncode, results[1].stdout, results[1].stderr))
        comparisons += 1

    for fixture in ["pres01", "wp3_modal_strengthen"]:
        results = []
        for base in [root, upstream]:
            paths = [base / "evals" / "fixtures" / (fixture + suffix + ".txt")
                     for suffix in ["_original", "_transformed"]]
            results.append(subprocess.run([sys.executable, "-B", str(base / "scripts" / "validate_preservation.py"),
                                           *map(str, paths)], capture_output=True))
        check((results[0].returncode, results[0].stdout, results[0].stderr) ==
              (results[1].returncode, results[1].stdout, results[1].stderr))
        comparisons += 1
print(f"NoCap smoke: {checks} assertions passed; {comparisons} English CLI comparisons matched upstream."
      if comparisons else f"NoCap smoke: {checks} assertions passed; English CLI comparisons skipped (baseline absent).")
