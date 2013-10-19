import counter
import random
import libtcodpy as libtcod
import colors
import console
from compositecore import Leaf, CompositeMessage


class Actor(Leaf):
    """
    An abstract component, enteties with this component can act.
    """
    def __init__(self):
        super(Actor, self).__init__()
        self.component_type = "actor"

    def act(self):
        """
        The action the parent component should do. And return energy spent.

        Subclasses should override this method.
        """
        pass


class KeyboardEventMover(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """

    def __init__(self):
        super(KeyboardEventMover, self).__init__()
        self._status_flags = set()
        self.component_type = "controler"

    def has_status(self, status):
        return status in self._status_flags


class Strength(Leaf):
    """
    Composites holding this has the strength attribute.
    """
    def __init__(self, strength):
        super(Strength, self).__init__()
        self.strength = strength
        self.component_type = "strength"


class IsPlayer(Leaf):
    """
    Component that marks the player.

    Only the player should have this component.
    """
    def __init__(self):
        super(IsPlayer, self).__init__()
        self.component_type = "is_player"


class AttackSpeed(Leaf):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, attack_speed):
        super(AttackSpeed, self).__init__()
        self.attack_speed = attack_speed
        self.component_type = "attack_speed"


class GameState(Leaf):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, value):
        super(GameState, self).__init__()
        self.value = value
        self.component_type = "game_state"


class MovementSpeed(Leaf):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, value):
        super(MovementSpeed, self).__init__()
        self.value = value
        self.component_type = "movement_speed"


class Faction(Leaf):
    """
    The faction attribute keeps track of the faction.

    All other factions are concidered hostile.
    """

    PLAYER = 0
    MONSTER = 1

    def __init__(self, faction):
        super(Faction, self).__init__()
        self.faction = faction
        self.component_type = "faction"


class CharPrinter(Leaf):
    def __init__(self):
        super(CharPrinter, self).__init__()
        self.component_type = "char_printer"
        self._status_cycle_colors = []
        self._blink_color_fg_queue = []

    def draw_no_effect(self, position):
        """
        Draws the char on the given position on the console.

        Bypasses all effects.
        """
        if(not self.parent.graphic_char.color_bg is None):
            console.console.set_color_bg(position,
                                         self.parent.graphic_char.color_bg)
        if(not self.parent.graphic_char.color_fg is None):
            console.console.set_color_fg(position,
                                         self.parent.graphic_char.color_fg)
        if(not self.parent.graphic_char.symbol is None):
            console.console.set_symbol(position,
                                       self.parent.graphic_char.symbol)

    def draw(self, position):
        """
        Draws the char on the given position on the console.
        """
        self.draw_no_effect(position)
        if(len(self._blink_color_fg_queue) > 0):
            console.console.set_color_fg(position,
                                         self._blink_color_fg_queue.pop())

    def draw_unseen(self, screen_position):
        """
        Draws the char as it looks like outside the field of view.
        """
        console.console.set_colors_and_symbol(screen_position,
                                              colors.UNSEEN_FG,
                                              colors.UNSEEN_BG,
                                              self.parent.graphic_char.symbol)

    def set_fg_blink_colors(self, colors):
        """
        Sets the foreground blink queue.

        These colors will be drawn as an effect,
        the regular colors won't be drawn until the blink queue is empty.
        """
        self._blink_color_fg_queue = colors


class GraphicChar(Leaf):
    """
    Composites holding this has a graphical representation as a char.
    """
    def __init__(self, color_bg, color_fg, symbol):
        super(GraphicChar, self).__init__()
        self.component_type = "graphic_char"
        self._symbol = symbol
        self._color_bg = color_bg
        self._color_fg = color_fg

    @property
    def symbol(self):
        return self._symbol

    @property
    def color_bg(self):
        return self._color_bg

    @property
    def color_fg(self):
        return self._color_fg

    def copy(self):
        """
        Makes a copy of this component.
        """
        return GraphicChar(self.color_bg, self.color_fg, self.symbol)


class GraphicCharTerrainCorners(GraphicChar):
    """
    Composites holding this has a graphical representation as a char.
    """
    def __init__(self, color_bg, color_fg, symbol, sticky_terrain_classes):
        super(GraphicCharTerrainCorners, self).__init__(color_bg, color_fg,
                                                        symbol)
        self._sticky_terrain_classes = sticky_terrain_classes
        self._wall_symbol_row = symbol
        self.has_calculated = False

    @property
    def symbol(self):
        if not self.has_calculated:
            self.calculate_wall_symbol()
        return self._symbol

    def calculate_wall_symbol(self):
        neighbours_mask = 0
        for index, neighbour in enumerate(self._get_neighbour_terrains()):
            if(any([terrain is neighbour.__class__
                   for terrain in self._sticky_terrain_classes])):
                neighbours_mask |= 2 ** index
        self._symbol = self._wall_symbol_row + neighbours_mask

    def _get_neighbour_terrains(self):
        tiles = (self.parent.dungeon_level.value.
                 get_tiles_surrounding_position(self.parent.position.value))
        return [tile.get_terrain() for tile in tiles]

    def copy(self):
        """
        Makes a copy of this component.
        """
        return GraphicChar(self.color_bg, self.color_fg, self.symbol)


class Description(Leaf):
    """
    Composites holding this has some describing text and a name.
    """
    def __init__(self, name="XXX_UNNAMED_XXX",
                 description="XXX_Description_XXX"):
        super(Description, self).__init__()
        self.name = name
        self.description = description
        self.component_type = "description"

    def copy(self):
        """
        Makes a copy of this component.
        """
        return Description(self.name, self.description)


class Path(Leaf):
    """
    Composites holding this has a path that it may step through.
    """
    def __init__(self):
        super(Description, self).__init__()
        self.path = None
        self.component_type = "path"

    def init_path(self):
        """
        Iniates the path using the dungeon map, from the DungeonMask module.
        """
        dungeon_map = self.DungeonMask.dungeon_map
        self.path = libtcod.path_new_using_map(dungeon_map, 1.0)

    def has_path(self):
        """
        Returns True if the entity has a path to walk.
        """
        if(self.path is None or libtcod.path_is_empty(self.path)):
            return False
        return True

    def try_step_path(self):
        """
        Tries to step the entity along the path, relies on the Mover module.
        """
        if(not self.has_path()):
            return False
        x, y = libtcod.path_walk(self.path, True)
        step_succeeded = self.Mover.try_move_to((x, y))
        return step_succeeded

    def set_path_to_random_walkable_point(self):
        positions = self.get_walkable_positions_from_my_position()
        destination = random.sample(positions, 1)[0]
        sx, sy = self.position
        dx, dy = destination
        libtcod.path_compute(self.path, sx, sy, dx, dy)

    def get_walkable_positions_from_my_position(self):
        dungeon_level = self.DungeonLevel.dungeon_level
        position = self.Position.position
        return dungeon_level.walkable_destinations.\
            get_walkable_positions_from_my_position(self.parent, position)

    def message(self, message):
        if(message == CompositeMessage.DUNGEON_LEVEL_CHANGED):
            self.init_path()


class Health(Leaf):
    """
    Health Component. Composites holding this has health points.

    Attributes:
        _health_counter (Counter): Holds the min, max and current health.
    """
    def __init__(self, max_hp):
        super(Health, self).__init__()
        self.component_type = "health"
        self.hp = counter.Counter(max_hp, max_hp)
        self.killer = None

    def hurt(self, damage, entity=None):
        """
        Damages the entity by reducing hp by damage.

        Args:
            damage: The ammount of damage caused.
            entity: The entity that caused the damage (if any)
        """
        self.hp.decrease(damage)
        self.GraphicChar.\
            set_fg_blink_colors([colors.LIGHT_PINK, colors.RED])
        if(self.is_dead()):
            self.killer = entity

    def heal(self, health):
        """
        Heals increases the current hp by health.

        Args:
            heal: The amount of health that was regained.
        """
        self.hp.increase(health)

    def is_dead(self):
        """
        Returns True if the entity is considered dead.
        """
        return self.hp.value == 0


ITEM_CAPACITY = 16


class Inventory(Leaf):
    """
    Holds the Items an entity is carrying.
    """
    def __init__(self):
        super(Inventory, self).__init__()
        self._items = []
        self._entity = self.parent
        self._item_capacity = ITEM_CAPACITY
        self.component_type = "inventory"

    @property
    def items(self):
        return self._items

    def try_add(self, item):
        """
        Tries to add an item to the inventory.

        Returns True on success otherwise False.
        """
        if(not self.has_room_for_item()):
            return False
        else:
            success = item.mover.try_remove_from_dungeon()
            if not success:
                raise Exception("ERROR: Tried to remove item: "
                                + str(item) + "but could not.")
            self._items.append(item)
            return True

    def has_room_for_item(self):
        """
        Returns true if the inventory has room for another item.
        """
        return len(self._items) + 1 <= self._item_capacity

    def can_drop_item(self, item):
        """
        Returns true if it is a legal action to drop the item.
        """
        return item.mover.can_move(self._entity.position,
                                   self._entity.dungeon_level)

    def try_drop_item(self, item):
        """
        Tries to drop an item to the ground.

        Returns True on success otherwise False.
        """
        drop_successful = item.mover.try_move(self._entity.position,
                                              self._entity.dungeon_level)
        if drop_successful:
            self.remove_item(item)
        return drop_successful

    def remove_item(self, item):
        """
        Removes item from the inventory.
        """
        self._items.remove(item)

    def has_item(self, item):
        """
        Returns true if the item instance is in the inventory, false otherwise.
        """
        return item in self._items

    def is_empty(self):
        """
        Returns true the inventory is empty, false otherwise.
        """
        return len(self._items) <= 0

    def items_of_equipment_type(self, type_):
        """
        Returns a list of all items in the inventory of the given type.
        """
        return [item for item in self._items
                if item.equipment_type.value == type_]
