import settings
import geometry as geo

FPS = 60

STATUS_BAR_WIDTH = 17
RIGHT_SIDE_MENU_WIDTH = 24

MONSTER_STATUS_BAR_WIDTH = 17
GAME_STATE_WIDTH = settings.WINDOW_WIDTH - (STATUS_BAR_WIDTH +
                                            MONSTER_STATUS_BAR_WIDTH)

MESSAGES_BAR_WIDTH = GAME_STATE_WIDTH
MESSAGES_BAR_HEIGHT = 16

GAME_STATE_HEIGHT = settings.WINDOW_HEIGHT - MESSAGES_BAR_HEIGHT

STATUS_BAR_HEIGHT = settings.WINDOW_HEIGHT
MONSTER_STATUS_BAR_HEIGHT = settings.WINDOW_HEIGHT

ITEMS_ALLOWED_PER_TILE = 1
ENTITIES_ALLOWED_PER_TILE = 1

AXIS_DIRECTIONS = {
    "E": geo.Vector2D(1, 0),
    "N": geo.Vector2D(0, 1),
    "W": geo.Vector2D(-1, 0),
    "S": geo.Vector2D(0, -1)
}

DIAGONAL_DIRECTIONS = {
    "NW": geo.Vector2D(-1, 1),
    "NE": geo.Vector2D(1, 1),
    "SW": geo.Vector2D(-1, -1),
    "SE": geo.Vector2D(1, -1)
}

CENTER_DIRECTION = geo.Vector2D(0, 0)

DIRECTIONS = dict(AXIS_DIRECTIONS.items() + DIAGONAL_DIRECTIONS.items())
DIRECTIONS_LIST = DIRECTIONS.values()
