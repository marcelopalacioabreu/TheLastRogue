import Counter as counter
import Colors as colors
import DungeonLevel as dungeonLevel
import libtcodpy as libtcod
import Entity as entity


# TODO move to settings.
move_controls = {
    't': (0, -1),  # up
    'h': (0, 1),   # down
    'd': (-1, 0),  # left
    'n': (1, 0),   # right
}


def wait_for_keypress():
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS,
                               key, mouse, False)
    key_char = get_key_char(key)
    return key_char


def get_key_char(key):
    if key.vk == libtcod.KEY_CHAR:
        return chr(key.c)
    else:
        return key.vk


class Player(entity.Entity):

    def __init__(self):
        super(Player, self).__init__()
        self.hp = counter.Counter(10, 10)
        self.fov_map = None
        self._sight_radius = 10
        self._memory_map = []

    @staticmethod
    def get_color_fg():
        return colors.DB_WHITE

    @staticmethod
    def get_symbol():
        return ord('@')

    def update(self, dungeonLevel, _):
        done = False
        while not done:
            key = wait_for_keypress()
            position = self.position
            if key in move_controls:
                dx, dy = move_controls[key]
                new_position = position + (dx, dy)
                move_succeded = self.try_move_to_position(dungeonLevel,
                                                          new_position)
                done = move_succeded
            elif key == libtcod.KEY_ESCAPE:
                self.kill()
                done = True
            elif key == 'r':  # Rest
                done = True
            elif key == 'p':  # Pick up
                done = True

    def get_memory_of_map(self, dungeon_level):
        self.set_memory_map_if_not_set(dungeon_level)
        return self._memory_map[dungeon_level.depth]

    def set_memory_map_if_not_set(self, dungeon_level):
        depth = dungeon_level.depth
        while(len(self._memory_map) <= depth):
            self._memory_map.append(None)
        if(self._memory_map[depth] is None):
            self._memory_map[depth] = dungeonLevel.unknown_level_map(
                dungeon_level.width, dungeon_level.height, dungeon_level.depth)

    def update_memory_of_tile(self, tile, x, y, depth):
        self._memory_map[depth].tile_matrix[y][x] = tile.copy()

    def update_fov_map(self):
        libtcod.map_compute_fov(self.fov_map,
                                self.position.x,
                                self.position.y,
                                self._sight_radius, True)
