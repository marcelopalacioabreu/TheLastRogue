import geometry
from compositecore import Leaf


class Vision(Leaf):
    """
    Holds functions that exposes what the parent entity can see.
    """
    def __init__(self):
        super(Vision, self).__init__()
        self.component_type = "vision"

    def get_seen_entities(self):
        """
        Gets all entities seen by this entity not including self.
        """
        seen_entities = []
        for entity in self.parent.dungeon_level.value.entities:
            if self.parent.dungeon_mask.can_see_point(entity.position.value):
                seen_entities.append(entity)
        return [entity for entity in seen_entities if not entity is self]

    def get_seen_entities_closest_first(self):
        """
        Gets all seen entities sorted on distance from self not including self.
        """
        return sorted(self.get_seen_entities(),
                      key=lambda entity:
                      geometry.chess_distance(self.parent.position.value,
                                              entity.position.value))

    def get_closest_seen_entity(self):
        """
        Gets the closest of all seen entities not including self.
        """
        closest_seen_entities = self.get_seen_entities_closest_first()
        if(len(closest_seen_entities) < 1):
            return None
        return closest_seen_entities[0]


class SightRadius(Leaf):
    """
    Composites holding this has the sight_radius attribute.
    """
    def __init__(self, sight_radius):
        super(SightRadius, self).__init__()
        self.component_type = "sight_radius"
        self.value = sight_radius