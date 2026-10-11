"""Offline tests for entity resolution."""

from continuity_editor.extraction.schemas import ExtractedEntity
from continuity_editor.retrieval.resolver import EntityResolver


def character(name, *aliases):
    return ExtractedEntity(name=name, kind="character", aliases=list(aliases))


def test_the_same_name_resolves_to_the_same_entity():
    resolver = EntityResolver("oz")
    first = resolver.resolve(character("the Scarecrow"))
    assert resolver.resolve(character("Scarecrow")).entity_id == first.entity_id


def test_part_of_a_longer_name_matches_when_only_one_entity_fits():
    resolver = EntityResolver("oz")
    woodman = resolver.resolve(character("the Tin Woodman"))
    assert resolver.resolve(character("the Woodman")).entity_id == woodman.entity_id
    wizard = resolver.resolve(character("the Great Oz"))
    assert resolver.resolve(character("Oz, the Great and Terrible")).entity_id == wizard.entity_id


def test_east_and_west_witches_stay_apart():
    resolver = EntityResolver("oz")
    east = resolver.resolve(character("the Wicked Witch of the East"))
    west = resolver.resolve(character("the Wicked Witch of the West"))
    assert east.entity_id != west.entity_id
    # "the Witch" fits both, so it is merged into neither.
    assert resolver.resolve(character("the Witch")).entity_id not in {east.entity_id, west.entity_id}


def test_a_near_identical_spelling_matches():
    resolver = EntityResolver("oz")
    woodman = resolver.resolve(character("the Tin Woodman"))
    assert resolver.resolve(character("the Tin Woodsman")).entity_id == woodman.entity_id


def test_a_character_and_a_place_never_merge():
    resolver = EntityResolver("oz")
    wizard = resolver.resolve(character("Oz"))
    land = resolver.resolve(ExtractedEntity(name="Oz", kind="location"))
    assert wizard.entity_id != land.entity_id


def test_a_world_element_matches_a_character_or_place_of_the_same_name():
    resolver = EntityResolver("oz")
    group = resolver.resolve(ExtractedEntity(name="the Munchkins", kind="world_element"))
    again = resolver.resolve(character("the Munchkins"))
    assert again.entity_id == group.entity_id
    assert type(again).__name__ == "WorldElement"  # keeps the kind it was first stored with


def test_only_name_like_aliases_are_used_for_matching():
    resolver = EntityResolver("oz")
    dorothy = resolver.resolve(character("Dorothy", "the girl"))
    wizard = resolver.resolve(character("Oz", "the Great Wizard"))
    assert resolver.resolve(character("the girl")).entity_id != dorothy.entity_id
    assert resolver.resolve(character("the Great Wizard")).entity_id == wizard.entity_id


def test_names_remember_the_first_name_used():
    resolver = EntityResolver("oz")
    lion = resolver.resolve(character("the Cowardly Lion"))
    resolver.resolve(character("the Lion"))
    assert resolver.names()[lion.entity_id] == "the Cowardly Lion"
