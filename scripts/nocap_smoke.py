#!/usr/bin/env python3
"""Offline NoCap checks. Run with python -B scripts/nocap_smoke.py."""
from pathlib import Path
import subprocess
import sys

from _lang import detect_language, polish_matching_view
from banned_phrase_scan import mask_ignored_spans, scan_for_violations
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
for phrase in [
    "warto zauważyć", "warto podkreślić", "należy zaznaczyć",
    "w dzisiejszym dynamicznym świecie", "dokonać oceny", "dokonał analizy",
    "dokonano wyboru", "przeprowadzić weryfikację", "wykonać sprawdzenie",
    "w celu dokonania", "celem przeprowadzenia", "na dzień dzisiejszy",
    "w dniu dzisiejszym", "trzeba podkreślić", "podkreślić należy",
    "podkreślenia wymaga", "odgrywa kluczową rolę",
    "odgrywają kluczową rolę", "odgrywał kluczową rolę", "odgrywała kluczową rolę",
    "odgrywały kluczową rolę", "odgrywali kluczową rolę", "kluczowa rola",
    "wykorzystać synergię", "uwolnić potencjał", "zaadresować problem",
    "zaadresować problemy", "zaadresować kwestię", "zaadresować kwestie",
    "zaadresowania problemu", "zaadresowania problemów", "zaadresowania kwestii",
    "jako model językowy", "mam nadzieję, że ta odpowiedź", "oto poprawiona wersja",
    "przełomowe rozwiązanie", "przełomowego rozwiązania", "przełomowym rozwiązaniem",
    "kompleksowe podejście", "kompleksowego podejścia", "kompleksowym podejściem",
    "niniejszym informujemy", "szanowni państwo",
]:
    for surface in [phrase, polish_matching_view(phrase).upper()]:
        hits = scan_for_violations("Hasło: " + surface, language="pl")
        check(len(hits) == 1 and hits[0]["phrase"] == surface and hits[0]["severity"] == "soft")
        check(scan_for_violations(f'„{surface}” `{surface}`', language="pl") == [])
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

# v0.2: ASCII/mixed prose follows the same source-offset and review contracts.
for text in ["Warto zauwazyc, ze API dziala", "Moze wystapic blad request timeout",
             "Nie dziala.", "Serwer.", "Kompleksowego podejscia do SDK",
             "Zaadresowania kwestii API", "Otrzyma 5 PLN."]:
    check(detect_language(text) == "pl")
for text in ["API", "SDK JSON HTTP", "PLN", "500 PLN", "Data model", "Model selection",
             "language model", "Amounts in PLN", "Role model", "Role selection", "SA",
             "The dedicated server checks the API request."]:
    check(detect_language(text) == "en")
for original in ["3,5 PLN", "500 PLN", "-3,5 zl"]:
    check(detect_language(original) == "en")
    check(any(c["type"] == "pl_currency" and c["value"] == original
              for c in extract_constraints(original)))
    changed = original.replace("5", "6")
    check(not validate_preservation(original, changed)["passed"])
    check(not validate_preservation(original, changed, [])["passed"])
for original in ["Kwota wynosi +3,5 PLN.", "+3,5 zl", "+3,5 zł", "3,5 pln", "3,5 ZŁ", "3,5zł"]:
    amount = original.removeprefix("Kwota wynosi ").removesuffix(".")
    check(any(c["type"] == "pl_currency" and c["value"] == amount and
              original[c["start"]:c["end"]] == amount for c in extract_constraints(original)))
    check(validate_preservation(original, original)["passed"])
    changed = original.replace("3,5", "3,6")
    check(not validate_preservation(original, changed)["passed"])
    check(not validate_preservation(original, changed, [])["passed"])
check(not validate_preservation("+3,5 PLN", "3,5 PLN")["passed"])
check(detect_language("bonjour merci") == "unknown")
check(validate_preservation("bonjour merci", "bonjour salut")["passed"])
check(scan_for_violations("Warto zauwazyc, ze API dziala", language="en") == [])
for text in ["Łódź İ SDK.\nŻółw: ODGRYWAJĄ KLUCZOWĄ ROLĘ w API.",
             "Łódź İ SDK.\nŻółw: ODGRYWAL KLUCZOWA ROLE w API."]:
    check(len(polish_matching_view(text)) == len(text))
    suggestion = build_suggestions(text)[0]
    span = suggestion["span"]
    check(span["start"] == text.index("ODGR"))
    check(span["text"] == text[span["start"]:span["end"]] == text.split(": ")[1].split(" w API")[0])
for protected in ['„Warto zauwazyc”', '`Warto zauwazyc`',
                  '~~~pl\nWarto zauwazyc\n~~~', '> Warto zauwazyc']:
    check(scan_for_violations(protected, language="pl") == [])
for text in [
    "Szanowni Państwo, warto zauważyć, że API działa.",
    "Niniejszym informujemy o odstąpieniu od umowy. Warto zauważyć, że zwracamy kwotę.",
    "Walidator odgrywa kluczową rolę: weryfikuje podpis JWT. Warto zauważyć, że API działa.",
    "Kluczowa rola administratora polega na nadawaniu uprawnień. Warto zauważyć, że API działa.",
    "Dedykowany serwer obsługuje API. Warto zauważyć, że API działa.",
    "Należy zaznaczyć pole wyboru przed wysłaniem request. Warto zauważyć, że API działa.",
    "Umowa: klient musi zapłacić. „Niniejszym informujemy” to cytat. Warto zauważyć, że API działa.",
]:
    for surface in [text, polish_matching_view(text)]:
        hits = scan_for_violations(surface)
        check(len(hits) == 1 and polish_matching_view(hits[0]["phrase"]).lower() == "warto zauwazyc")
check(bool(scan_for_violations("Niniejszym informujemy o kompleksowym podejściu do umowy.")))
check(bool(scan_for_violations("API odgrywa kluczową rolę w sukcesie firmy.")))
check(scan_for_violations("Zaadresować problematyczny kod.", language="pl") == [])

# v0.3 auto routing reaches each new family and retains English headings.
for source, category in [
    ("Zespol dokonal oceny ofert.", "pl_nominalization"),
    ("W celu dokonania wyboru porownaj oferty.", "pl_purpose"),
    ("Na dzien dzisiejszy brak odpowiedzi.", "pl_time"),
    ("Podkreślenia wymaga wynik badania.", "pl_emphasis"),
]:
    check(any(hit["category"] == category for hit in scan_for_violations(source)))
check(detect_language("Model selection and data analysis") == "en")

# v0.3: candidate phrases stay bounded; context and source meaning decide edits.
for source, phrase, category in [
    ("Zespół dokonał oceny ofert.", "dokonał oceny", "pl_nominalization"),
    ("W celu dokonania wyboru porównaj oferty.", "W celu dokonania", "pl_purpose"),
    ("Na dzień dzisiejszy brak odpowiedzi.", "Na dzień dzisiejszy", "pl_time"),
    ("Trzeba podkreślić, że serwer działa.", "Trzeba podkreślić", "pl_emphasis"),
]:
    hits = scan_for_violations(source, language="pl")
    check(any(hit["phrase"] == phrase and hit["category"] == category for hit in hits))
for source, category in [
    ("Biegły ma dokonać oceny oddziaływania na środowisko.", "pl_nominalization"),
    ("Dane przetwarzamy w celu dokonania oceny ryzyka z art. 6.", "pl_purpose"),
]:
    hits = scan_for_violations(source, language="pl")
    check(len(hits) == 1 and hits[0]["category"] == category and hits[0]["severity"] == "soft")
for source in [
    "„Na dzień dzisiejszy” to cytat z formularza.",
    "Podkreślić należy tekst i zapisać plik.",
]:
    check(scan_for_violations(source, language="pl") == [])
source = "Łódź.\nŻółw: W CELU DOKONANIA wyboru."
hits = scan_for_violations(source, language="pl")
check(len(hits) == 1 and hits[0]["phrase"] == "W CELU DOKONANIA" and hits[0]["column"] == 7)
check(source.index(hits[0]["phrase"]) == source.index("W CELU"))

source = "Wedlug Anny zaden klient nie moze zaplacic tylko 1 234,56 zl 12 pazdziernika 2026, jesli Piotr podpisze umowe."
check(detect_language(source) == "pl")
check(validate_preservation(source, source)["warnings"] == [])
for old, new, marker in [("zaden ", "", "negation"), ("moze", "musi", "modality"),
                         ("jesli", "poniewaz", "condition"), ("tylko ", "", "scope"),
                         ("Wedlug ", "", "attribution")]:
    check(any(marker in w for w in validate_preservation(source, source.replace(old, new))["warnings"]))
for cue in ["jezeli", "chyba ze", "pod warunkiem", "o ile", "z wyjatkiem"]:
    original = "API dziala " + cue + " klient wysle request."
    check(any("condition" in w for w in validate_preservation(original, original.replace(cue, "bo"))["warnings"]))
for original in [source, "Kwota wynosi powyzej -3,5 zl.", "Termin: 12 wrzesnia 2026."]:
    check(validate_preservation(original, original, [], language="pl")["passed"])
    for constraint in extract_constraints(original, "pl"):
        check(original[constraint["start"]:constraint["end"]] == constraint["value"])
for original, old, new in [(source, "1 234,56 zl", "1 234,57 zl"),
                            (source, "pazdziernika", "wrzesnia"),
                            ("Kwota wynosi powyzej -3,5 zl.", "powyzej ", ""),
                            ("Kwota wynosi -3,5 zl.", "-", "")]:
    changed = original.replace(old, new)
    check(not validate_preservation(original, changed, [], language="pl")["passed"])
    start = original.index(old)
    edits = [{"span": {"start": start, "end": start + len(old), "text": old},
              "suggested_replacement": new}]
    check(any(f["gate"] == "accept-all" for f in check_suggestions(original, edits, reviewed=True)))
cleanup = "Warto zauwazyc, ze API dziala."
span_text = "Warto zauwazyc, ze "
edits = [{"span": {"start": 0, "end": len(span_text), "text": span_text}, "suggested_replacement": ""}]
check(any(f["gate"] == "agent-review" for f in check_suggestions(cleanup, edits)))
check(check_suggestions(cleanup, edits, reviewed=True) == [])
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
