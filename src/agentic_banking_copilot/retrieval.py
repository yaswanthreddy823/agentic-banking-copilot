"""Hybrid retrieval: keyword overlap + TF-IDF, with a rerank step.

Deliberately dependency-free so the demo runs offline. The point of this
module is not a novel retriever — it is that retrieval is measured:
every answer carries its cited documents and a confidence score, and the
eval harness reports top-1 citation accuracy on a held-out-style set.
"""

from __future__ import annotations

import math
import re
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "what", "how", "do", "does",
    "can", "i", "you", "we", "for", "to", "of", "in", "on", "and", "or",
    "my", "me", "please", "tell", "about", "with", "by", "at", "from",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


class Retriever:
    """TF-IDF retriever over the synthetic knowledge base."""

    def __init__(self, documents: list[dict]):
        self.documents = documents
        self.doc_tokens: list[Counter] = []
        self.doc_freq: Counter = Counter()
        for doc in documents:
            tokens = Counter(tokenize(doc["title"] + " " + doc["text"]))
            self.doc_tokens.append(tokens)
            for token in tokens:
                self.doc_freq[token] += 1
        self.n_docs = len(documents)

    def _idf(self, token: str) -> float:
        return math.log((1 + self.n_docs) / (1 + self.doc_freq.get(token, 0))) + 1.0

    def score(self, query_tokens: list[str], doc_idx: int) -> float:
        doc = self.doc_tokens[doc_idx]
        total = 0.0
        for token in query_tokens:
            if token in doc:
                # Title matches count double: titles are strong topic signals.
                title_tokens = set(tokenize(self.documents[doc_idx]["title"]))
                boost = 2.0 if token in title_tokens else 1.0
                total += boost * (1 + math.log(doc[token])) * self._idf(token)
        return total

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Return top_k documents with score and a 0-1 confidence proxy.

        Confidence is a saturating function of the raw TF-IDF score so it
        is comparable across queries: 1 - exp(-score / 8).
        """
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        scored = []
        for idx, doc in enumerate(self.documents):
            raw = self.score(query_tokens, idx)
            if raw > 0:
                scored.append((raw, doc))
        # Rerank: exact phrase overlap in the document text breaks ties.
        query_lower = query.lower()
        scored.sort(
            key=lambda item: (
                item[0] + (2.0 if query_lower in item[1]["text"].lower() else 0.0)
            ),
            reverse=True,
        )
        results = []
        for raw, doc in scored[:top_k]:
            results.append(
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "text": doc["text"],
                    "score": round(raw, 3),
                    "confidence": round(1 - math.exp(-raw / 8.0), 3),
                }
            )
        return results


def extract_answer_sentences(doc_text: str, query: str, max_sentences: int = 2) -> list[str]:
    """Extractive answer: sentences from the cited doc that overlap the query.

    Keeping answers extractive is intentional for a compliance setting:
    the agent quotes policy instead of paraphrasing it into a new claim.
    """
    query_tokens = set(tokenize(query))
    sentences = [s.strip() for s in doc_text.split(". ") if s.strip()]
    scored = []
    for sentence in sentences:
        overlap = len(query_tokens & set(tokenize(sentence)))
        scored.append((overlap, sentence))
    scored.sort(key=lambda item: item[0], reverse=True)
    picked = [s for overlap, s in scored if overlap > 0][:max_sentences]
    if not picked and sentences:
        picked = [sentences[0]]
    return [s if s.endswith(".") else s + "." for s in picked]
