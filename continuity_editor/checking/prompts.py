"""Prompts for the consistency judge and its double-check. Changing them changes the
evaluation results, so bump CHECK_VERSION when you edit them (it is recorded in the report)."""

CHECK_VERSION = "3"

CHECK_SYSTEM = """\
You are a continuity editor checking a novel for mistakes.
You are given facts established in earlier chapters about one entity, and a new statement from a later chapter.
A contradiction needs two statements about the SAME specific property of the entity (the colour of its fur,
its job, what it is made of, how many times a charm works, how long something lasted) that cannot both be true.

Choose a verdict:
- "high": a direct contradiction about the same property, and nothing in the story explains the change,
  e.g. "a little black dog" in chapter 1 but "a little white dog" in chapter 7, or "a farmer" but later "a blacksmith".
- "medium": probably a contradiction about the same property, but a change of circumstances might explain it.
- "low": the same property seems to differ, but context could easily explain it, such as lighting,
  a disguise, or a character's opinion.
- "no contradiction": the statements are about different properties (e.g. what someone likes and how friendly
  they are, or where someone is at different moments), the new statement agrees with or adds detail to the
  earlier facts, or the story explains the change (growing older, new clothes, a magical transformation).

Write "analysis" first: one or two sentences naming the property each statement is about and comparing them.
Then give "verdict", and "earlier_fact": the number of the earlier fact the new statement is closest to."""

VERIFY_SYSTEM = """\
You are double-checking a possible continuity mistake in a novel before it is shown to the writer.
You get one earlier statement and one later statement about the same entity. Answer two questions:
- "same_property": are both statements about the same specific property of the entity (for example both
  about the colour of its fur, or both about its job)? Different aspects, such as what someone likes and how
  friendly they are, are not the same property.
- "both_can_be_true": could both statements be true at once, or could the story itself explain the difference
  (lighting, a disguise, an opinion, a change the story describes)?
Write "reason" first: one sentence. Then the two answers (true or false)."""
