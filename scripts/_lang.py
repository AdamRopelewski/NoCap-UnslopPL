#!/usr/bin/env python3
"""Shared cheap English-detection helpers for banned_phrase_scan.py,
structure_scan.py, and silhouette_scan.py. All three scanners must decline the
same non-English inputs, so this table and its two functions live in exactly
one place.

Also home to the shared prose-view helpers (tokenizer, markdown stripper,
paragraph splitter) used by structure_scan.py and silhouette_scan.py. Those
two scanners previously carried private copies of these functions that had
drifted from each other (structure blanked blockquote lines, silhouette
didn't; silhouette stripped **bold**, structure didn't). strip_markdown_for_prose
below is the UNION of both original code paths, gated behind flags so each
caller reconciles the drift deliberately rather than silently: structure_scan
passes blank_blockquotes=True, silhouette_scan passes strip_bold=True."""

from __future__ import annotations

import re


# A small set of high-frequency English function words used only for a cheap
# language check. The words are chosen to be distinctively English: Spanish,
# French, German, etc. rarely use them, so their share of tokens is a robust
# signal without a language-model dependency.
ENGLISH_FUNCTION_WORDS = frozenset({
    "the", "and", "is", "are", "was", "were", "of", "to", "in", "that", "it",
    "for", "with", "on", "this", "but", "not", "you", "have", "be", "as", "at",
    "or", "we", "they", "will", "would", "there", "their", "what", "which",
    "when", "from", "been", "has", "had", "its", "an", "by", "our", "your",
    "if", "than", "then", "them", "these", "those", "about", "into", "over",
    "after", "before", "how", "why", "where", "who", "can", "could", "should",
    "do", "does", "did", "so", "out", "just", "more", "most", "some", "such",
    "only", "also", "because", "while", "between", "through", "during", "being",
})


def english_function_share(text: str) -> float:
    """Share of word tokens that are common English function words."""
    tokens = re.findall(r"[a-z']+", text.lower())
    if not tokens:
        return 1.0
    hits = sum(1 for t in tokens if t in ENGLISH_FUNCTION_WORDS)
    return hits / len(tokens)


def is_probably_english(text: str, threshold: float = 0.10, min_tokens: int = 15) -> bool:
    """Cheap English detector backing a graceful non-English decline.

    Conservative on purpose: inputs below ``min_tokens`` are always treated as
    English (too little signal to decline), and ``threshold`` is low enough that
    even terse or ESL-flavored English clears it. Only prose with almost no
    English function words (i.e. another language) is declined.
    """
    tokens = re.findall(r"[a-z']+", text.lower())
    if len(tokens) < min_tokens:
        return True
    return english_function_share(text) >= threshold


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text.lower())


def strip_markdown_for_prose(
    text: str, *, blank_blockquotes: bool = False, strip_bold: bool = False
) -> str:
    """Strip markdown structure down to a prose view for cadence/discourse
    metrics. UNION of structure_scan's and silhouette_scan's original
    strippers -- each original branch is preserved verbatim, gated behind the
    flag that reproduces that caller's exact prior behavior.

    blank_blockquotes=True reproduces structure_scan's prior strip (blanks
    both blockquote and heading lines in one combined check). strip_bold=True
    reproduces silhouette_scan's prior strip (also collapses **bold** markers
    after list/ordinal stripping).
    """
    text = re.sub(r"```[\s\S]*?```", "\n\n", text)
    kept = []
    for line in text.splitlines():
        if blank_blockquotes:
            if re.match(r"\s*>", line) or re.match(r"\s{0,3}#{1,6}\s+", line):
                kept.append("")
                continue
        else:
            if re.match(r"\s{0,3}#{1,6}\s+", line):
                kept.append("")  # drop heading text from the prose view
                continue
        line = re.sub(r"^\s*[-*+]\s+", "", line)
        line = re.sub(r"^\s*\d+[.)]\s+", "", line)
        if strip_bold:
            line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        kept.append(line)
    return "\n".join(kept)


def paragraphs(
    text: str, *, blank_blockquotes: bool = False, strip_bold: bool = False
) -> list[str]:
    stripped = strip_markdown_for_prose(
        text, blank_blockquotes=blank_blockquotes, strip_bold=strip_bold
    )
    return [
        re.sub(r"\s+", " ", p).strip()
        for p in re.split(r"\n\s*\n", stripped)
        if p.strip()
    ]


_POLISH_ASCII = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")


def polish_matching_view(text: str) -> str:
    """Map only Polish letters, one character to one; keep source offsets."""
    return text.translate(_POLISH_ASCII)


POLISH_WORDS = frozenset(polish_matching_view("""
nie jest są się oraz dla przez przy jeśli jeżeli chyba może można musi należy
warto podkreślić zaznaczyć zauważyć niniejszym szanowni państwo dziękuję
pytanie odpowiedź świecie dzisiejszym dynamicznym zmieniającym kluczową rolę
synergię potencjał przełomowe rozwiązanie kompleksowe podejście jako
językowy sztuczna inteligencja umowę kwotę wynosi mln kosztuje działa błąd
użytkownik użytkownika dane danych tylko każdy wszystkie nigdy bez
tak cześć zaadresować oto poprawiona wersja
zostanie proszę płaci przekazuje według zdaniem powiedział twierdzi
że żeby ponieważ gdy który która które którego których więc również
już jeszcze będzie był była było były został została zwraca zwracają
obsługuje żądanie żądania odpowiedzi serwer klienta usługi umowy kwota
odgrywa odgrywają odgrywał odgrywała odgrywały odgrywali kluczowa rola
kluczowej roli kompleksowego podejścia kompleksowym podejściem
zaadresowania kwestię kwestii problemu problemów problemami
wystąpić występuje otrzyma podpisze zapłacić żaden żadna żadne
wedle powinien powinna muszą mogą warunkiem wyjątkiem koszt
dokonać dokonał dokonała dokonali dokonano dokonuje dokonują dokonujemy
oceny analizy wyboru przeglądu przeprowadzić przeprowadził przeprowadzono
przeprowadza przeprowadzają analizę ocenę weryfikację wykonać wykonał
wykonano wykonuje wykonują sprawdzenie celu celem dokonania wykonania
przeprowadzenia dzień dzisiejszy trzeba podkreślenia wymaga
""").split())
_FOREIGN_WORDS = frozenset("""
bonjour merci ceci cette avec dans pour une est les des vous nous pas
hola gracias esto una los las para pero con que por el
hallo danke und ist sind nicht das die der ein eine mit für
привет это для что как спасибо 你好 这是 谢谢
""".split())


def detect_language(text: str, language: str | None = None) -> str:
    """Route prose to en/pl/unknown; an explicit override resolves ambiguity."""
    if language not in (None, "auto", "en", "pl"):
        raise ValueError("language must be auto, en or pl")
    if language in ("en", "pl"):
        return language
    prose = re.sub(r"```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`", " ", text)
    tokens = re.findall(r"[^\W\d_]+", prose.lower())
    # ASCII role/SA also occur in English; accented rolę/są retain their evidence.
    pl = sum(t not in {"role", "sa"} and polish_matching_view(t) in POLISH_WORDS for t in tokens)
    en = sum(t in ENGLISH_FUNCTION_WORDS for t in tokens)
    foreign = sum(t in _FOREIGN_WORDS for t in tokens)
    # shortcut: lexical routing leaves ambiguous fragments, use --language for them.
    if pl and pl > foreign and pl >= en:
        return "pl"
    if foreign > en or (not en and re.search(r"[\u0400-\u052f\u3400-\u9fff]", prose)):
        return "unknown"
    if en or all(t.isascii() for t in tokens):
        return "en"
    return "unknown"


def unavailable(language: str, feature: str) -> dict:
    """An unavailable metric supplies no evidence about prose quality."""
    return {"language": language, "available": False,
            "reason": f"{feature} is validated for English only",
            "flags": [], "metrics": {}, "penalty": None}
