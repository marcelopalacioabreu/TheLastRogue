import random

from animation import animate_fall, animate_fall_sync
from attacker import DamageTypes
from compositecommon import EntityShareTileEffect
from compositecore import Leaf, Composite
import entityeffect
from graphic import GraphicChar, CharPrinter, GraphicCharTerrainCorners
import messenger
from mover import Mover
from position import Position, DungeonLevel
from prompt import PromptPlayer
from stats import Flag, DataPoint, DataTypes, GamePieceTypes
from statusflags import StatusFlags
import colors
import icon


class TerrainFactory(object):
    def __init__(self):
        self.wall = None
        self.floor = None

    def get_wall(self):
        if self.wall is None:
            self.wall = Wall()
        return self.wall

    def get_floor(self):
        if self.floor is None:
            self.floor = Floor()
        return self.floor


terrain_factory = TerrainFactory()


class BumpAction(Leaf):
    """
    Defines what happens if the player bumps into this terrain.
    """
    def __init__(self):
        super(BumpAction, self).__init__()
        self.component_type = "bump_action"

    def bump(self, source_entity):
        pass

    def can_bump(self, source_entity):
        return True


def set_terrain_components(terrain):
    terrain.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
    terrain.set_child(Mover())
    terrain.set_child(Position())
    terrain.set_child(DungeonLevel())
    terrain.set_child(CharPrinter())


class Floor(Composite):
    FLOOR_FLAG = "is_floor"

    def __init__(self):
        super(Floor, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.FLOOR_BG,
                                   colors.FLOOR_FG,
                                   icon.CENTER_DOT))
        self.set_child(CharPrinter())
        self.set_child(Flag(Floor.FLOOR_FLAG))


class Water(Composite):
    def __init__(self):
        super(Water, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.BLUE_D,
                                   colors.BLUE,
                                   icon.WATER))
        self.set_child(CharPrinter())


class GlassWall(Composite):
    def __init__(self):
        super(GlassWall, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.FLOOR_BG, colors.WHITE, icon.GLASS_WALL))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_solid"))


class Chasm(Composite):
    def __init__(self):
        super(Chasm, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.BLACK, colors.DARKNESS, icon.CHASM2))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_chasm"))

        self.set_child(PlayerFallDownChasmAction())
        self.set_child(FallRemoveNonPlayerNonFlying())
        self.set_child(PromptPlayerChasm())


class PromptPlayerChasm(PromptPlayer):
    def __init__(self):
        super(PromptPlayerChasm, self).__init__(messenger.WANT_TO_JUMP_DOWN_CHASM)
        self.component_type = "prompt_player_chasm"


class FallRemoveNonPlayerNonFlying(EntityShareTileEffect):
    def __init__(self):
        super(FallRemoveNonPlayerNonFlying, self).__init__()
        self.component_type = "non_player_fall_down_chasm_share_tile_effect"

    def effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        terrain = target_entity.dungeon_level.value.get_tile_or_unknown(target_entity.position.value).get_terrain()
        animate_fall(target_entity, terrain)
        target_entity.mover.try_remove_from_dungeon()

    def can_effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        if target_entity.has("status_flags"):
            return not target_entity.has("is_player") and not target_entity.status_flags.has_status(StatusFlags.FLYING)
        else:
            return not target_entity.has("is_player")


class PlayerFallDownChasmAction(EntityShareTileEffect):
    def __init__(self):
        super(PlayerFallDownChasmAction, self).__init__()
        self.component_type = "player_fall_down_chasm_share_tile_effect"

    def effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        animate_fall_sync(target_entity)
        current_depth = target_entity.dungeon_level.value.depth
        dungeon = target_entity.dungeon_level.value.dungeon
        next_dungeon_level = dungeon.get_dungeon_level(current_depth + 1)
        target_position = next_dungeon_level.get_random_walkable_position_in_dungeon(target_entity)
        target_entity.mover.move_push_over(target_position, next_dungeon_level)
        self._fall_damage(target_entity)

    def can_effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        return target_entity.has("is_player") and not target_entity.status_flags.has_status(StatusFlags.FLYING)

    def _fall_damage(self, target_entity):
        min_damage = 2
        max_damage = 5
        damage = random.randrange(min_damage, max_damage + 1)
        damage_effect = entityeffect.UndodgeableAttackEntityEffect(None, damage,
                                                                   [DamageTypes.FALL], messenger.FALL_DOWN_MESSAGE)
        target_entity.effect_queue.add(damage_effect)


class Unknown(Composite):
    def __init__(self):
        super(Unknown, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(CharPrinter())
        self.set_child(GraphicChar(colors.BLACK,
                                   colors.BLACK,
                                   ' '))
        self.set_child(Flag("is_unknown"))
        self.set_child(Flag("is_solid"))


class Wall (Composite):
    def __init__(self):
        super(Wall, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(CharPrinter())
        self.set_child(GraphicCharTerrainCorners(colors.FLOOR_BG,
                                                 colors.WALL_FG,
                                                 icon.CAVE_WALLS_ROW2,
                                                 [Wall, Door, Chasm]))
        self.set_child(Flag("is_solid"))
        self.set_child(Flag("is_opaque"))
        self.set_child(Flag("is_wall"))


class Door(Composite):
    def __init__(self):
        super(Door, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(CharPrinter())
        self.set_child(GraphicChar(colors.FLOOR_BG,
                                   colors.ORANGE_D,
                                   icon.DOOR))
        self.set_child(Flag("is_solid"))
        self.set_child(Flag("is_opaque"))

        self.set_child(OpenDoorAction())
        self.set_child(OpenDoorBumpAction())
        self.set_child(Flag("is_door"))


class OpenDoorAction(Leaf):
    """Opens the door terrain."""
    def __init__(self):
        super(OpenDoorAction, self).__init__()
        self.component_type = "open_door_action"

    def open_door(self):
        if self.parent.has("is_solid"):
            self.parent.remove_component_of_type("is_solid")
        if self.parent.has("is_opaque"):
            self.parent.remove_component_of_type("is_opaque")
        self.parent.graphic_char.icon = icon.DOOR_OPEN
        self.parent.dungeon_level.value.signal_terrain_changed(self.parent.position.value)


class OpenDoorBumpAction(BumpAction):
    """
    Defines what happens if the player bumps into this terrain.
    """
    def __init__(self):
        super(OpenDoorBumpAction, self).__init__()
        self.component_type = "bump_action"

    def bump(self, source_entity):
        self.parent.open_door_action.open_door()

    def can_bump(self, source_entity):
        return (self.parent.has("is_solid") and
                (source_entity.status_flags.
                 has_status(StatusFlags.CAN_OPEN_DOORS)))
