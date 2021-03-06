from compositecore import Leaf, CompositeMessage


class Position(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self):
        super(Position, self).__init__()
        self.component_type = "position"
        self._value = (-1, -1)

    @property
    def value(self):
        """
        Gets the dungeon_level the entity is currently in.
        """
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        if self.has_parent() and not self.value is None:
            self.parent.send_message(CompositeMessage.POSITION_CHANGED)


class DungeonLevel(Leaf):
    """
    Composites holding this is in a DungeonLevel.
    """
    def __init__(self):
        super(DungeonLevel, self).__init__()
        self.component_type = "dungeon_level"
        self._value = None
        self.last_dungeon_level = None

    @property
    def value(self):
        """
        Gets the dungeon_level the entity is currently in.
        """
        return self._value

    @value.setter
    def value(self, new_dungeon_level):
        """
        Sets current dungeon_level of the entity.
        Also updates the visibility/solidity of the dungeon_level tiles.
        """
        if not self._value is new_dungeon_level:
            old_dungeon_level = self._value
            self._value = new_dungeon_level
            self._signal_dungeon_level_changed()
            if(not old_dungeon_level is None and
               self.has_sibling("actor")):
                old_dungeon_level.remove_actor_if_present(self.parent)
                self.last_dungeon_level = old_dungeon_level
        if self.last_dungeon_level is None:
            self.last_dungeon_level = new_dungeon_level

    def _signal_dungeon_level_changed(self):
        """
        Is called when dungeon level has changed.
        """
        if self.has_parent() and not self.value is None:
            self.parent.send_message(CompositeMessage.DUNGEON_LEVEL_CHANGED)
            if self.has_sibling("actor"):
                self.value.add_actor_if_not_present(self.parent)
            if self.has_sibling("is_dungeon_feature"):
                self.value.add_dungeon_feature_if_not_present(self.parent)

    def on_parent_changed(self):
        """
        When the parent changes try to add it to the dungeon.
        """
        self._signal_dungeon_level_changed()
