"""Local keyword search: BM25F over skill fields, with stemming, prefix
matching, phrase bonus and config-driven synonym expansion. No skill names
are hardcoded here; synonyms come from config/synonyms.yaml."""
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import yaml

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[+#][a-z0-9+#]*)?")
STOPWORDS = frozenset("""
a an and are as at be by can do does for from has have how i in into is it its me my of on or our
so that the their them then there these this to us use used uses using want we what when where which
who will with you your need needs should would could please help find get make some any all
""".split())

# Field weights for BM25F; name dominates, body contributes least.
FIELD_WEIGHTS = {"name": 4.0, "tags": 2.5, "category": 2.0, "description": 2.0, "body": 1.0}
K1, B = 1.2, 0.75
SYNONYM_WEIGHT = 0.6
PREFIX_WEIGHT = 0.5
PHRASE_BONUS = 0.35      # relative boost when the whole query appears as a phrase
NAME_EXACT_BONUS = 1.0
NAME_COVERAGE_BOOST = 1.5  # multiplier scale for query terms found in the skill name
NAME_BIGRAM_BOOST = 0.3   # per query bigram that appears contiguously in the name
MAX_BODY_CHARS = 30_000

_SUFFIXES = ("ational", "ations", "ation", "ators", "ator", "ities", "ity", "ings", "ing",
             "ers", "er", "ies", "ied", "ate", "es", "ed", "s", "e")


def stem(word: str) -> str:
    if len(word) <= 3 or not word.isalpha():
        return word
    for suf in _SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            base = word[: -len(suf)]
            if suf in ("ies", "ied"):
                base += "y"
            if len(base) > 3 and base[-1] == base[-2] and base[-1] not in "aeiouls":
                base = base[:-1]  # planner -> plann -> plan
            return base
    return word


def tokenize(text: str, keep_stop: bool = False) -> list[str]:
    toks = TOKEN_RE.findall(text.lower())
    return [stem(t) for t in toks if keep_stop or t not in STOPWORDS]


@dataclass
class Synonyms:
    groups: list[list[tuple[str, ...]]] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path | None) -> "Synonyms":
        if not path or not Path(path).is_file():
            return cls()
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        groups = []
        for g in data.get("groups", []):
            members = [tuple(tokenize(str(m), keep_stop=True)) for m in g]
            members = [m for m in members if m]
            if len(members) > 1:
                groups.append(members)
        return cls(groups)

    def expand(self, q: list[str]) -> dict[str, tuple[str, ...]]:
        """Map each extra stem implied by q to the query stems that triggered it."""
        extra: dict[str, tuple[str, ...]] = {}
        for members in self.groups:
            hits = [m for m in members if _contains(q, m)]
            if not hits:
                continue
            trigger = tuple(dict.fromkeys(t for m in hits for t in m))
            for m in members:
                for t in m:
                    if t not in q and t not in STOPWORDS and t not in extra:
                        extra[t] = trigger
        return extra


def _contains(seq: list[str], sub: tuple[str, ...]) -> bool:
    n = len(sub)
    return any(tuple(seq[i:i + n]) == sub for i in range(len(seq) - n + 1))


@dataclass
class Doc:
    id: str
    fields: dict[str, Counter]
    lengths: dict[str, int]
    phrase_text: str          # lower-cased name + description + body, whitespace-normalized
    name_norm: str


class SearchIndex:
    def __init__(self, skills, synonyms: Synonyms):
        self.synonyms = synonyms
        self.docs: dict[str, Doc] = {}
        df: Counter = Counter()
        totals: Counter = Counter()
        for s in skills:
            texts = {
                "name": f"{s.name} {s.id.replace('-', ' ')}",
                "tags": " ".join(s.tags),
                "category": s.category,
                "description": s.description,
                "body": s.body[:MAX_BODY_CHARS],
            }
            fields = {f: Counter(tokenize(t)) for f, t in texts.items()}
            lengths = {f: sum(c.values()) for f, c in fields.items()}
            for f, n in lengths.items():
                totals[f] += n
            for term in set().union(*[set(c) for c in fields.values()]):
                df[term] += 1
            phrase = " ".join(tokenize(f"{s.name} {s.description} {s.body[:MAX_BODY_CHARS]}", keep_stop=True))
            self.docs[s.id] = Doc(s.id, fields, lengths, phrase, " ".join(tokenize(s.id.replace("-", " "), keep_stop=True)))
        n = max(len(self.docs), 1)
        self.avg_len = {f: (totals[f] / n) or 1.0 for f in FIELD_WEIGHTS}
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}
        self.vocab = sorted(self.idf)

    def _prefix_terms(self, term: str) -> list[str]:
        if len(term) < 4:
            return []
        return [v for v in self.vocab if v != term and v.startswith(term)][:20]

    def _tf(self, doc: Doc, term: str) -> tuple[float, list[str]]:
        score, fields = 0.0, []
        for f, w in FIELD_WEIGHTS.items():
            tf = doc.fields[f].get(term, 0)
            if tf:
                norm = tf / (1 - B + B * doc.lengths[f] / self.avg_len[f])
                score += w * norm
                fields.append(f)
        return score, fields

    def search(self, query: str, candidate_ids=None, limit: int = 10, offset: int = 0) -> tuple[int, list[dict]]:
        q_all = tokenize(query, keep_stop=True)
        q = [t for t in dict.fromkeys(tokenize(query)) if t]
        if not q:
            return 0, []
        # term -> (weight, query stems it stands for)
        weighted: dict[str, tuple[float, tuple[str, ...]]] = {t: (1.0, (t,)) for t in q}
        for t, trig in self.synonyms.expand(q_all).items():
            weighted.setdefault(t, (SYNONYM_WEIGHT, trig))
        for t in list(q):
            for p in self._prefix_terms(t):
                weighted.setdefault(p, (PREFIX_WEIGHT, (t,)))
        phrase = " ".join(q_all)
        ids = candidate_ids if candidate_ids is not None else self.docs.keys()

        results = []
        for sid in ids:
            doc = self.docs[sid]
            score, matched_q, matched_fields, why_terms = 0.0, set(), set(), []
            name_hits: set[str] = set()
            for term, (w, origins) in weighted.items():
                idf = self.idf.get(term)
                if not idf:
                    continue
                tf, flds = self._tf(doc, term)
                if not tf:
                    continue
                score += w * idf * (tf * (K1 + 1)) / (tf + K1)
                matched_fields.update(flds)
                why_terms.append(term)
                matched_q.update(origins)
                if "name" in flds:
                    name_hits.update(origins)
            if score <= 0:
                continue
            coverage = len(matched_q & set(q)) / len(q)
            score *= 0.5 + 0.5 * coverage  # reward matching more of the query
            bonus = []
            name_cov = len(name_hits & set(q)) / len(q)
            if name_cov:
                score *= 1 + NAME_COVERAGE_BOOST * name_cov
                bonus.append(f"{round(name_cov * 100)}% of query in name")
            name_toks = doc.name_norm.split()
            for a, b in zip(q_all, q_all[1:]):
                if any(name_toks[i] == a and name_toks[i + 1] == b for i in range(len(name_toks) - 1)):
                    score *= 1 + NAME_BIGRAM_BOOST
            if len(q_all) > 1 and phrase in doc.phrase_text:
                score *= 1 + PHRASE_BONUS
                bonus.append("exact phrase")
            if phrase == doc.name_norm or phrase.replace(" ", "-") == sid:
                score += NAME_EXACT_BONUS * 10
                bonus.append("exact name")
            results.append((score, sid, sorted(matched_fields, key=list(FIELD_WEIGHTS).index), why_terms, coverage, bonus))

        results.sort(key=lambda r: (-r[0], r[1]))
        total = len(results)
        out = []
        for score, sid, flds, terms, coverage, bonus in results[offset: offset + limit]:
            reason = f"Matched {', '.join(dict.fromkeys(terms[:6]))} in {', '.join(flds)}"
            if coverage < 1:
                reason += f" ({round(coverage * 100)}% of query terms)"
            if bonus:
                reason += "; " + ", ".join(bonus)
            out.append({"id": sid, "score": round(score, 3), "reason": reason})
        return total, out
