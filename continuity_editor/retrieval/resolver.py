"""Entity resolution: map the names a chapter uses onto entities already in the story bible.

A new name matches a known entity when, ignoring case and a leading "the", "a" or "an":
1. it equals the known name or one of its alias names; or
2. its words are all part of the known name, or the other way round, and only one known
   entity fits ("the Woodman" -> "the Tin Woodman", "the Great Oz" -> "Oz, the Great and
   Terrible"; "the Witch" stays separate when there are several witches); or
3. it is a near-identical spelling ("Tin Woodsman" -> "Tin Woodman").
Names that differ by a whole word, like "Witch of the East" and "Witch of the West", never
match. Anything else becomes a new entity.

Rules 2 and 3 compare only entities of the same kind. Rule 1 also lets a "world_element"
match a character or place of the same name, because a small model labels things like
"the Munchkins" or "the Emerald City" inconsistently; a character and a place never merge
("Oz" is both the Wizard and the land). Only aliases that look like names (capitalised, e.g.
"the Great Wizard") are used for matching: descriptions such as "the girl" or "the road"
would pull unrelated entities together.
"""

import re
from dataclasses import dataclass, field

from rapidfuzz import fuzz

from continuity_editor.extraction.schemas import ExtractedEntity
from continuity_editor.graph.connection import Neo4jConnection
from continuity_editor.graph.models import Character, Entity, Location, WorldElement

SPELLING_MIN_SCORE = 85  # per word: "woodsman"/"woodman" is 93, "west"/"east" is 75
_ARTICLE = re.compile(r"^(the|a|an)\s+", re.IGNORECASE)
_STOPWORDS = {"the", "a", "an", "of", "and"}
_MODEL_FOR_KIND: dict[str, type[Entity]] = {
    "character": Character,
    "location": Location,
    "world_element": WorldElement,
}
_KIND_FOR_LABEL = {"Character": "character", "Location": "location", "WorldElement": "world_element"}


def name_key(name: str) -> str:
    return _ARTICLE.sub("", name.strip()).casefold()


def _words(key: str) -> frozenset[str]:
    return frozenset(w for w in re.findall(r"[a-z0-9']+", key) if w not in _STOPWORDS)


@dataclass
class KnownEntity:
    entity_id: str
    kind: str
    name: str
    keys: set[str] = field(default_factory=set)


class EntityResolver:
    def __init__(self, novel_id: str) -> None:
        self.novel_id = novel_id
        self.known: list[KnownEntity] = []

    @classmethod
    def from_graph(cls, conn: Neo4jConnection, novel_id: str) -> "EntityResolver":
        """A resolver that knows every entity already stored for `novel_id`."""
        resolver = cls(novel_id)
        rows = conn.query(
            """
            MATCH (e:Entity {novel_id: $novel_id})
            RETURN e.entity_id AS entity_id, e.name AS name, coalesce(e.aliases, []) AS aliases,
                   [label IN labels(e) WHERE label <> 'Entity'][0] AS label
            """,
            novel_id=novel_id,
        )
        for row in rows:
            keys = {name_key(row["name"])} | {name_key(a) for a in row["aliases"] if _looks_like_a_name(a)}
            resolver.known.append(KnownEntity(row["entity_id"], _KIND_FOR_LABEL[row["label"]], row["name"], keys))
        return resolver

    def resolve(self, entity: ExtractedEntity) -> Entity:
        """The graph entity for `entity`: a known one if it matches, otherwise a new one.

        The name used in this chapter is remembered as an alias either way, so later chapters
        that use it match directly.
        """
        key = name_key(entity.name)
        match = self._find(entity.kind, key)
        if match is None:
            new = _MODEL_FOR_KIND[entity.kind](novel_id=self.novel_id, name=entity.name, aliases=entity.aliases)
            entity_id = new.entity_id
            taken = {k.entity_id for k in self.known}
            while entity_id in taken:  # same slug as a different entity: keep them apart
                entity_id += "_2"
            match = KnownEntity(entity_id, entity.kind, entity.name)
            self.known.append(match)
        match.keys |= {key, *(name_key(a) for a in entity.aliases if _looks_like_a_name(a))}
        # The stored entity keeps the kind it was first seen with.
        model = _MODEL_FOR_KIND[match.kind]
        return model(novel_id=self.novel_id, name=entity.name, aliases=entity.aliases, entity_id=match.entity_id)

    def names(self) -> dict[str, str]:
        """entity_id -> the name the entity was first stored under."""
        return {k.entity_id: k.name for k in self.known}

    def _find(self, kind: str, key: str) -> KnownEntity | None:
        compatible = [k for k in self.known if k.kind == kind or "world_element" in (k.kind, kind)]
        exact = [k for k in compatible if key in k.keys]
        if exact:
            return next((k for k in exact if k.kind == kind), exact[0])
        candidates = [k for k in self.known if k.kind == kind]
        words = _words(key)
        if words:
            fits = [k for k in candidates if any(_fits(words, _words(kk)) for kk in k.keys)]
            if len(fits) == 1:
                return fits[0]
        close = [k for k in candidates if any(_near_spelling(key, kk) for kk in k.keys)]
        return close[0] if len(close) == 1 else None


def _looks_like_a_name(alias: str) -> bool:
    stripped = _ARTICLE.sub("", alias.strip())
    return stripped[:1].isupper()


def _fits(a: frozenset[str], b: frozenset[str]) -> bool:
    return bool(a and b) and (a <= b or b <= a)


def _near_spelling(a: str, b: str) -> bool:
    """The same words in the same order, allowing a small spelling difference inside a word
    ("Woodsman"/"Woodman") but not a different word ("East"/"West" is only 75% alike)."""
    words_a = [w for w in re.findall(r"[a-z0-9']+", a) if w not in _STOPWORDS]
    words_b = [w for w in re.findall(r"[a-z0-9']+", b) if w not in _STOPWORDS]
    return (
        bool(words_a)
        and len(words_a) == len(words_b)
        and all(fuzz.ratio(x, y) >= SPELLING_MIN_SCORE for x, y in zip(words_a, words_b))
    )
