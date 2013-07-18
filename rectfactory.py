import geometry as geo
import settings
import constants


def full_screen_rect():
    return geo.Rect(geo.zero2d(),
                    settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)


def center_of_screen_rect(width, height):
    return ratio_of_screen_rect(width, height, 0.5, 0.5)


def ratio_of_screen_rect(width, height, x_ratio, y_ratio):
    x = (settings.WINDOW_WIDTH - width) * x_ratio
    y = (settings.WINDOW_HEIGHT - height) * y_ratio
    return geo.Rect(geo.Vector2D(x, y), width, height)


def right_side_menu_rect():
    x = settings.WINDOW_WIDTH - constants.RIGHT_SIDE_MENU_WIDTH
    y = 0
    return geo.Rect(geo.Vector2D(x, y),
                    constants.RIGHT_SIDE_MENU_WIDTH,
                    settings.WINDOW_HEIGHT)


def message_display_rect():
    message_display_position =\
        geo.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH,
                        constants.GAME_STATE_HEIGHT)
    return geo.Rect(message_display_position,
                    constants.MESSAGES_BAR_WIDTH,
                    constants.MESSAGES_BAR_HEIGHT)


def player_status_rect():
    status_bar_position =\
        geo.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH +
                     constants.GAME_STATE_WIDTH, 0)
    return geo.Rect(status_bar_position, constants.STATUS_BAR_WIDTH,
                    constants.STATUS_BAR_HEIGHT)

    x = settings.WINDOW_WIDTH - constants.RIGHT_SIDE_MENU_WIDTH
    y = 0
    return geo.Rect(geo.Vector2D(x, y),
                    constants.RIGHT_SIDE_MENU_WIDTH,
                    settings.WINDOW_HEIGHT)