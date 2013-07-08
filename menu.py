import inputhandler
import colors
import gui
import vector2d
import gamestate
import settings
import game


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class Menu(gamestate.GameState):
    def __init__(self, position, width, height):
        super(Menu, self).__init__()
        self._menu_items = ["XX_Menu_Item_XX"]
        self._selected_index = 0
        self._wrap = True
        self.position = position
        self.width = width
        self.height = height
        self.may_escape = True
        self._item_stack_panel = gui.StackPanelVertical(vector2d.ZERO,
                                                        self.width,
                                                        colors.INTERFACE_BG,
                                                        vertical_space=1)

    def update(self):
        if(not self.has_valid_option_selected()):
            self._selected_index = 0
            if(not self.has_valid_option_selected()):
                gamestate.game_state_stack.pop()
                return
        key = inputhandler.get_keypress()
        if key == inputhandler.UP:
            self.index_decrease()
        if key == inputhandler.DOWN:
            self.index_increase()
        if key == inputhandler.ENTER:
            self.activate()
        if key == inputhandler.ESCAPE and self.may_escape:
            gamestate.game_state_stack.pop()

        self._recreate_option_list()

    def has_valid_option_selected(self):
        return 0 <= self._selected_index < len(self._menu_items)

    def _update_menu_items(self):
        pass

    def _recreate_option_list(self):
        self._update_menu_items()
        self._item_stack_panel.elements = []
        for index, item in enumerate(self._menu_items):
            if(index == self._selected_index):
                color = colors.TEXT_ACTIVE
            else:
                color = colors.TEXT_INACTIVE
            menu_item = gui.TextBox(item, vector2d.ZERO, color)
            self._item_stack_panel.elements.append(menu_item)

    def activate(self):
        pass

    def index_increase(self):
        self._offset_index(1)

    def index_decrease(self):
        self._offset_index(-1)

    def _offset_index(self, offset):
        if(len(self._menu_items) == 0):
            return
        if(self._wrap):
    # Will behave strangely for when offset is less than -menu_size
            self._selected_index =\
                (offset + self._selected_index + len(self._menu_items))\
                % len(self._menu_items)
        else:
            self._selected_index = clamp(offset + self._selected_index, 0,
                                         len(self._menu_items) - 1)

    def draw(self):
        self._item_stack_panel.draw(self.position)


class MainMenu(Menu):
    def __init__(self, position, width, height):
        super(MainMenu, self).__init__(position, width, height)
        self.start_game_option = "Start Game"
        self.quit_option = "Quit"
        self._menu_items = [self.start_game_option, self.quit_option]
        self.rectangle_bg = gui.Rectangle(vector2d.ZERO, width,
                                          height, colors.INTERFACE_BG)

    def activate(self):
        selected_option = self._menu_items[self._selected_index]
        if(selected_option == self.start_game_option):
            new_game = game.Game()
            gamestate.game_state_stack.push(new_game)
        elif(selected_option == self.quit_option):
            gamestate.game_state_stack.pop()

    def draw(self):
        self.rectangle_bg.draw()
        draw_position = vector2d.Vector2D(0, settings.WINDOW_HEIGHT - 7)
        self._item_stack_panel.draw(draw_position)


class InventoryMenu(Menu):
    def __init__(self, position, width, height, player):
        super(InventoryMenu, self).__init__(position, width, height)
        self._player = player
        self.rectangle_bg = gui.Rectangle(vector2d.ZERO, width,
                                          height, colors.INTERFACE_BG)
        self.rectangle_screen_grey =\
            gui.RectangleGray(vector2d.ZERO,
                              settings.WINDOW_WIDTH,
                              settings.WINDOW_HEIGHT,
                              colors.DB_OPAL)
        heading = gui.TextBox("Inventory:", vector2d.ZERO,
                              colors.INVENTORY_HEADING,
                              margin=vector2d.Vector2D(0, 1))
        self._inventory_stack_panel =\
            gui.StackPanelVertical(vector2d.ZERO,
                                   width,
                                   colors.INTERFACE_BG)
        self._inventory_stack_panel.elements.append(heading)
        self._inventory_stack_panel.elements.append(self._item_stack_panel)

    def activate(self):
        item = self._player.inventory.items[self._selected_index]
        if(len(item.actions) >= 1):  # No actions no need for menu.
            item_actions_menu = ItemActionsMenu(self.position, self.width,
                                                self.height, item,
                                                self._player)
            gamestate.game_state_stack.push(item_actions_menu)

    def _update_menu_items(self):
        self._menu_items = [item.name for item in self._player.inventory.items]

    def draw(self):
        self.rectangle_screen_grey.draw(vector2d.ZERO)
        self.rectangle_bg.draw(self.position)
        self._inventory_stack_panel.draw(self.position)


class ItemActionsMenu(Menu):
    def __init__(self, position, width, height, item, player):
        super(ItemActionsMenu, self).__init__(position, width, height)
        self._menu_items = [action.name for action in item.actions]
        self.rectangle_bg = gui.Rectangle(vector2d.ZERO, width,
                                          height, colors.INTERFACE_BG)
        self.item = item
        self.player = player

    def activate(self):
        selected_action = self.item.actions[self._selected_index]
        selected_action.act(self.player, self.player)
        gamestate.game_state_stack.pop()

    def draw(self):
        self.rectangle_bg.draw()
        draw_position = vector2d.Vector2D(0, settings.WINDOW_HEIGHT - 7)
        self._item_stack_panel.draw(draw_position)
