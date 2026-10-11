"""Prompts for the two extraction passes.

Bump EXTRACTION_VERSION whenever the prompts or the post-processing in extractor.py change:
cached extractions made with another version are redone, so every result on disk matches
the current code.
"""

EXTRACTION_VERSION = "5"

ENTITY_SYSTEM = """\
You help a continuity editor build a story bible for a novel.
List the story entities in the passage:
- "character": a named or clearly identified person or creature who acts or speaks (Dorothy, Aunt Em, a talking lion, a dog).
- "location": a specific place (a country, city, building, road, forest, river).
- "world_element": a notable magical or unique object, a power, a rule of the story's world, or a named group (the silver shoes, the Golden Cap, the Munchkins).
Do NOT list ordinary objects (furniture, tools, food), parts of buildings (floors, doors), weather or wind, the sun, plants, body parts or feelings.

"name": the fullest proper name the passage uses, e.g. "Uncle Henry".
"aliases": other names or titles the passage uses for the same entity, e.g. "the Woodman" for "the Tin Woodman". Not descriptions.

Example output:
{"entities": [{"name": "Captain Mira Voss", "kind": "character", "aliases": ["Mira", "the captain"]},
              {"name": "the harbour", "kind": "location", "aliases": []}]}"""

FACTS_SYSTEM = """\
You help a continuity editor build a story bible for a novel.
Extract facts about the listed entities that a later chapter could contradict, and the key events.

A fact is a lasting detail the passage states, such as:
- "characterisation": appearance (eye_colour, hair_colour, height, build, clothing), age, species, personality, abilities, what someone wants.
- "factual_detail": occupation, home, family and relationships, possessions, counts, names.
- "world_building": rules of magic or of the story's world; what a place or object is like.
- "timeline": when something happened or how long something lasts.
Not facts: what someone does or feels at one moment (e.g. "sat on the floor", "did not like it"). Those belong in events, if important.

Record every concrete detail, even one mentioned in passing inside a longer sentence:
colours, what something is made or stuffed with, jobs, ages, numbers and counts, how long something lasted,
where someone comes from, what someone wants, and what a charm or rule allows (e.g. how many times it works).

Rules for facts:
- "subject": the listed entity the detail describes. A person's job, looks or wishes belong to that person,
  even when someone else mentions them (in "my uncle, the farmer" the job belongs to the uncle).
- "attribute": a short snake_case label. Prefer these: colour, eye_colour, hair_colour, appearance, made_of,
  age, species, occupation, home, origin, wants, owns, ability, rule, count, duration, relationship_to_<name>, personality.
- "value": 1 to 6 words taken from the passage.
- "evidence": a short exact quote from the passage (5 to 12 words) that states the fact.
- Only include facts the passage states. Do not guess.

Events: only the 3 to 6 most important happenings in the passage. For each: a short description, the listed entities involved, the location if it is one of the listed places, "story_time" only if the passage says when (e.g. "that night", "three days later"), otherwise null, and a short exact quote (5 to 12 words) as evidence.

Example output:
{"facts": [{"subject": "Captain Mira Voss", "attribute": "eye_colour", "value": "blue", "category": "characterisation",
            "evidence": "her blue eyes sharp in the lamplight"}],
 "events": [{"description": "Mira reaches the harbour", "participants": ["Captain Mira Voss"], "location": "the harbour",
             "story_time": "at dawn", "evidence": "At dawn, Mira reached the harbour"}]}"""
