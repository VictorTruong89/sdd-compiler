"""F2 CT-2.1 `keywords` — computed by code, never by a model (F2 D4, F5 D8).

A cheap retrieval signal for F5: lower-cased word tokens of the node's text,
minus one fixed, versioned English stop-word list, sorted and unique. Pure
numbers are left out; amounts are compared as quantities instead. Changing the
list changes every node's keywords, so it carries a version.
"""
from __future__ import annotations

import re

STOP_WORDS_VERSION = "en-1"

STOP_WORDS = frozenset("""
a about above after again against all am an and any are as at be because been before being
below between both but by can could did do does doing down during each few for from further
had has have having he her here hers herself him himself his how i if in into is it its itself
just me more most my myself no nor not now of off on once only or other our ours ourselves out
over own same she should so some such than that the their theirs them themselves then there
these they this those through to too under until up very was we were what when where which
while who whom why will with would you your yours yourself yourselves
must shall may might
""".split())

_TOKEN = re.compile(r"[a-z0-9]+")


def keywords(text: str) -> list[str]:
    tokens = {
        token for token in _TOKEN.findall(text.lower())
        if not token.isdigit() and token not in STOP_WORDS
    }
    return sorted(tokens)
