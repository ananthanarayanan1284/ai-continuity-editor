"""Step 3: resolve the entities a new chapter mentions and pull their earlier facts from the graph."""

from continuity_editor.retrieval.history import PriorFact, fact_history
from continuity_editor.retrieval.resolver import EntityResolver, name_key

__all__ = ["EntityResolver", "PriorFact", "fact_history", "name_key"]
