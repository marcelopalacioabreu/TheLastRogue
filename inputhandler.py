import libtcodpy as libtcod
import geometry as geo
import Queue
import time
from threading import Thread

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3
NORTHWEST = 4
NORTHEAST = 5
SOUTHWEST = 6
SOUTHEAST = 7
ENTER = 104
REST = 105
ONE = 106
TWO = 107
THREE = 108
FOUR = 109
FIVE = 110
ESCAPE = 111
PICKUP = 112
INVENTORY = 113
EXAMINE = 114
SHIFT = 115
DESCEND = 116
ZERO = 117
FIRE = 118

#Aliases:
UP = NORTH
DOWN = SOUTH
LEFT = WEST
RIGHT = EAST

KEY_SHIFT = libtcod.KEY_SHIFT

# TODO move to settings.
move_controls = {
    NORTH: geo.Vector2D(0, -1),
    SOUTH: geo.Vector2D(0, 1),
    WEST: geo.Vector2D(-1, 0),
    EAST: geo.Vector2D(1, 0),
    NORTHWEST: geo.Vector2D(-1, -1),
    NORTHEAST: geo.Vector2D(1, -1),
    SOUTHWEST: geo.Vector2D(-1, 1),
    SOUTHEAST: geo.Vector2D(1, 1)
}

controls = {
    't': NORTH,  # up
    libtcod.KEY_UP: NORTH,  # up
    libtcod.KEY_KP8: NORTH,  # up

    'h': SOUTH,   # down
    libtcod.KEY_DOWN: SOUTH,  # up
    libtcod.KEY_KP2: SOUTH,  # up

    'd': WEST,  # left
    libtcod.KEY_LEFT: WEST,  # left
    libtcod.KEY_KP4: WEST,  # up

    'n': EAST,   # right
    libtcod.KEY_RIGHT: EAST,  # right
    libtcod.KEY_KP6: EAST,  # up

    'g': NORTHWEST,   # up, left
    libtcod.KEY_KP7: NORTHWEST,  # up, left

    'c': NORTHEAST,   # up, right
    libtcod.KEY_KP9: NORTHEAST,  # up, right

    'm': SOUTHWEST,   # down, left
    libtcod.KEY_KP1: SOUTHWEST,  # down, left

    'w': SOUTHEAST,   # down, right
    libtcod.KEY_KP3: SOUTHEAST,  # down, right

    'f': FIRE,

    libtcod.KEY_ENTER: ENTER,
    libtcod.KEY_ESCAPE: ESCAPE,
    libtcod.KEY_SHIFT: SHIFT,  # shift

    "r": REST,
    "p": PICKUP,
    "i": INVENTORY,
    "x": EXAMINE,
    ">": DESCEND,
    libtcod.KEY_0: ZERO,
    libtcod.KEY_1: ONE,
    libtcod.KEY_2: TWO,
    libtcod.KEY_3: THREE,
    libtcod.KEY_4: FOUR,
    libtcod.KEY_5: FIVE,
}


class InputHandler(object):
    def __init__(self):
        self._input_queue = Queue.Queue()

    def get_keypress(self):
        if(not self._input_queue.empty()):
            return self._input_queue.get()
        return None

    def start_listener_thread(self):
        thread = Thread(target=self._get_keypress_loop)
        thread.daemon = True
        thread.start()

    def _get_keypress_loop(self):
# Oh God why is this needed?
        time.sleep(1)
        while True:
            while(self._input_queue.empty()):
                #key = libtcod.console_check_for_keypress()
                key = libtcod.console_wait_for_keypress(True)
                key_char = self._get_key_char(key)
                if key_char in controls.keys() and key.pressed:
                    self._input_queue.put(controls[key_char])
                #time.sleep(0.01)

    def _get_key_char(self, key):
        if key.vk == libtcod.KEY_CHAR:
            return chr(key.c).lower()  # Case insensetive
        else:
            return key.vk

    def is_special_key_pressed(self, special_key):
        if special_key in controls.keys():
            return libtcod.console_is_key_pressed(special_key)
        return False

handler = InputHandler()
handler.start_listener_thread()
