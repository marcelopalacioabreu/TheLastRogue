import math
import constants
from equipment import EquipmentSlots
import symbol

from messenger import messenger
from console import console
import colors
import geometry as geo
import turn
import style
import settings


class UIElement(object):
    def __init__(self, margin=geo.zero2d()):
        self.margin = margin
        self.parent = None

    def draw(self, offset=geo.zero2d()):
        pass

    def update(self):
        pass

    @property
    def height(self):
        return 0

    @property
    def width(self):
        return 0

    @property
    def total_height(self):
        return self.height + self.margin[1] * 2

    @property
    def total_width(self):
        return self.width + self.margin[0] * 2


class VerticalSpace(UIElement):
    def __init__(self, height, margin=geo.zero2d()):
        super(VerticalSpace, self).__init__(margin)
        self._height = height

    @property
    def height(self):
        return self._height


class HorizontalLine(UIElement):
    def __init__(self, symbol, color_fg, color_bg, width, margin=geo.zero2d()):
        super(HorizontalLine, self).__init__(margin)
        self.symbol = symbol
        self.color_bg = color_bg
        self.color_fg = color_fg
        self._width = width

    @property
    def height(self):
        return 1

    @property
    def width(self):
        return self._width

    def draw(self, offset=geo.zero2d()):
        """
        Draws the line.
        """
        x, y = geo.add_2d(offset, self.margin)
        for i in range(self.width):
            if (not self.symbol is None):
                console.set_symbol((x + i, y), self.symbol)
            if (not self.color_bg is None):
                console.set_color_bg((x + i, y), self.color_bg)
            if (not self.color_fg is None):
                console.set_color_fg((x + i, y), self.color_fg)


class RectangularUIElement(UIElement):
    def __init__(self, rect, margin=geo.zero2d()):
        super(RectangularUIElement, self).__init__(margin)
        self.rect = rect

    @property
    def height(self):
        return int(self.rect.height)

    @property
    def width(self):
        return int(self.rect.width)

    @property
    def offset(self):
        return geo.int_2d(self.rect.top_left)


class FilledRectangle(RectangularUIElement):
    def __init__(self, rect, color_bg, margin=geo.zero2d()):
        super(FilledRectangle, self).__init__(rect, margin)
        self.color_bg = color_bg

    def draw(self, offset=geo.zero2d()):
        px, py = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        for y in range(py, self.height + py):
            for x in range(px, self.width + px):
                console.set_color_bg((x, y), self.color_bg)
                console.set_symbol((x, y), ' ')


class StyledRectangle(RectangularUIElement):
    def __init__(self, rect, rect_style, title=None,
                 title_color_fg=colors.GRAY_D, margin=geo.zero2d()):
        super(StyledRectangle, self).__init__(rect, margin)
        self.style = rect_style
        self.title = title
        self.title_color_fg = title_color_fg

    def draw(self, offset=geo.zero2d()):
        px, py = geo.int_2d(geo.add_2d(geo.add_2d(offset, self.offset),
                                       self.margin))

        for y in range(py, self.height + py):
            for x in range(px, self.width + px):
                char_visual = self._get_char_visual(x - offset[0], y - offset[1])
                StyledRectangle.draw_char(x, y, char_visual)
        self._draw_title(offset)

    def _get_char_visual(self, x, y):
        if x == self.rect.left:
            if y == self.rect.top:
                return self.style.top_left
            elif y == self.rect.bottom - 1:
                return self.style.bottom_left
            else:
                return self.style.left
        if x == self.rect.right - 1:
            if y == self.rect.top:
                return self.style.top_right
            elif y == self.rect.bottom - 1:
                return self.style.bottom_right
            else:
                return self.style.right
        else:
            if y == self.rect.top:
                return self.style.top
            elif y == self.rect.bottom - 1:
                return self.style.bottom
            else:
                return self.style.center

    @staticmethod
    def draw_char(x, y, char_visual):
        console.set_colors_and_symbol((x, y), char_visual.color_fg,
                                      char_visual.color_bg, char_visual.symbol)

    def _draw_title(self, offset=geo.zero2d()):
        if not self.title is None:
            if len(self.title) % 2 == 1:
                self.title += " "
            y = offset[1] + self.rect.top
            title_length = (self.rect.width - len(self.title) - 2)
            x_offset = self.rect.top_left[0] + title_length / 2 + offset[0]
            StyledRectangle.draw_char(x_offset, y, self.style.title_separator_left)
            x_offset += 1
            console.set_default_color_fg(self.title_color_fg)
            console.print_text((x_offset, y), self.title)
            x_offset += len(self.title)
            StyledRectangle.draw_char(x_offset, y, self.style.title_separator_right)


class RectangleChangeColor(FilledRectangle):
    def __init__(self, rect, color_bg,
                 color_fg=colors.INACTIVE_GAME_FG, margin=geo.zero2d()):
        super(RectangleChangeColor, self).__init__(rect, color_bg, margin)
        self.color_fg = color_fg

    def draw(self, offset=geo.zero2d()):
        px, py = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        for y in range(py, self.height + py):
            for x in range(px, self.width + px):
                console.set_color_bg((x, y), self.color_bg)
                console.set_color_fg((x, y), self.color_fg)


class UIElementList(object):
    def __init__(self, elements):
        super(UIElementList, self).__init__()
        self.elements = elements

    def draw(self, offset=geo.zero2d()):
        for element in self.elements:
            element.draw(offset)

    def update(self):
        for element in self.elements:
            element.update()


class StackPanel(UIElement):
    def __init__(self, offset, margin=geo.zero2d()):
        super(StackPanel, self).__init__(margin=margin)
        self._offset = offset

    def append(self, element):
        element.parent = self
        return self._elements.append(element)

    def clear(self):
        for element in self._elements:
            element.parent = None
        self._elements = []

    @property
    def offset(self):
        return self._offset

    @property
    def rectangle(self):
        return geo.Rect(self.offset, self.width, self.height)

    def update(self):
        for element in self._elements:
            element.update()


class StackPanelHorizontal(StackPanel):
    def __init__(self, offset, margin=geo.zero2d(), horizontal_space=0):
        super(StackPanelHorizontal, self).__init__(offset, margin=margin)
        self.horizontal_space = horizontal_space
        self._elements = []

    @property
    def height(self):
        if len(self._elements) < 1:
            return 0
        return max([element.total_height for element in self._elements])

    @property
    def width(self):
        return sum([element.total_width + self.horizontal_space
                    for element in self._elements])

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        element_position = position
        for element in self._elements:
            element.draw(element_position)
            element_position = geo.add_2d(element_position,
                                          (element.total_width +
                                           self.horizontal_space, 0))


class StackPanelVertical(StackPanel):
    def __init__(self, offset, margin=geo.zero2d(), vertical_space=0):
        super(StackPanelVertical, self).__init__(offset, margin=margin)
        self.vertical_space = vertical_space
        self._elements = []

    @property
    def width(self):
        if len(self._elements) < 1:
            return 0
        return max([element.total_width for element in self._elements])

    @property
    def height(self):
        return sum([element.total_height + self.vertical_space
                    for element in self._elements])

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        element_position = position
        for element in self._elements:
            element.draw(element_position)
            element_position = geo.add_2d(element_position,
                                          (0, element.total_height +
                                              self.vertical_space))


class StackPanelVerticalCentering(StackPanelVertical):
    def __init__(self, offset, margin=geo.zero2d(), vertical_space=0):
        super(StackPanelVerticalCentering, self).__init__(offset,
                                                          margin=margin)

    def draw(self, offset=geo.zero2d()):
        root_x, y = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        for element in self._elements:
            x = root_x + (self.width - element.width + 1) / 2
            element.draw((x, y))
            y = y + element.total_height + self.vertical_space


class PlayerStatusBox(RectangularUIElement):
    def __init__(self, rect, player, margin=geo.zero2d()):
        super(PlayerStatusBox, self).__init__(rect, margin)
        self._player = player
        self._status_stack_panel = StackPanelVertical(rect.top_left, (1, 2))

        element_width = self.width - style.interface_theme.margin[0] * 2 - 2
        player_hp = player.health.hp
        hp_bar = CounterBarWithNumbers(player_hp, element_width,
                                       colors.HP_BAR_FULL, colors.HP_BAR_EMPTY,
                                       colors.WHITE)
        heart = SymbolUIElement((0, 0), symbol.HEART, colors.RED)

        self._hp_stack_panel = StackPanelHorizontal((0, 0), (0, 1), 1)
        self._hp_stack_panel.append(heart)
        self._hp_stack_panel.append(hp_bar)

        self._rectangle_bg = \
            StyledRectangle(rect, style.interface_theme.rect_style,
                            player.description.name, player.graphic_char.color_fg)

        self._status_stack_panel.append(self._hp_stack_panel)
        items_row = StackPanelHorizontal((0, 0), (2, 1), 1)
        items_row.append(InventoryBox(player.inventory, geo.Rect((0, 0), 10, 6)))
        items_row.append(EquipmentBox(player.equipment, geo.Rect((0, 0), 5, 6)))
        self._status_stack_panel.append(items_row)

        self.depth_text_box = TextBox("", (2, 0), colors.BLUE_D)
        self._status_stack_panel.append(self.depth_text_box)

    def update(self):
        self._status_stack_panel.update()
        self.depth_text_box.text = ("Depth:" +
                                    str(self._player.dungeon_level.value.depth + 1).rjust(4))

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(offset, self.margin)
        self._rectangle_bg.draw(position)
        self._status_stack_panel.draw(position)


class EquipmentBox(RectangularUIElement):
    POSITIONS = {
        EquipmentSlots.HEADGEAR: (2, 1),
        EquipmentSlots.LEFT_RING: (1, 2),
        EquipmentSlots.AMULET: (2, 2),
        EquipmentSlots.RIGHT_RING: (3, 2),
        EquipmentSlots.MELEE_WEAPON: (1, 3),
        EquipmentSlots.ARMOR: (2, 3),
        EquipmentSlots.RANGED_WEAPON: (3, 3),
        EquipmentSlots.BOOTS: (2, 4)}

    def __init__(self, equipment, rect, margin=geo.zero2d(), vertical_space=0):
        super(EquipmentBox, self).__init__(rect, margin=margin)
        self._equipment = equipment
        self._bg_rect = StyledRectangle(rect, style.MinimalStyle())
        self._equipment_slot_items = []

    def update(self):
        self._equipment_slot_items = []
        for slot in EquipmentSlots.ALL:
            if self._equipment.slot_is_equiped(slot):
                item = self._equipment.get(slot)
                graphic_item = SymbolUIElement(EquipmentBox.POSITIONS[slot],
                                               item.graphic_char.symbol,
                                               item.graphic_char.color_fg)
            else:
                graphic_item = SymbolUIElement(EquipmentBox.POSITIONS[slot],
                                               slot.symbol, colors.BLUE_D)
            self._equipment_slot_items.append(graphic_item)

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(offset, self.margin)
        self._bg_rect.draw(position)

        for graphic_item in self._equipment_slot_items:
            graphic_item.draw(position)


class InventoryBox(RectangularUIElement):
    def __init__(self, inventory, rect, margin=geo.zero2d(), vertical_space=0):
        super(InventoryBox, self).__init__(rect, margin=margin)
        self._inventory = inventory
        self._inventory_width = rect.width - 2
        self._inventory_height = rect.height - 2
        self._bg_rect = StyledRectangle(rect, style.ChestStyle())
        self.graphic_char_items = []

    def update(self):
        items = self._inventory.get_items_sorted()
        self.graphic_char_items = []
        for idx, item in enumerate(items):
            offset = (idx % self._inventory_width, idx / self._inventory_width)
            graphic_item = SymbolUIElement(offset, item.graphic_char.symbol,
                                           item.graphic_char.color_fg)
            self.graphic_char_items.append(graphic_item)

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(offset, self.margin)
        self._bg_rect.draw(position)
        for graphic_item in self.graphic_char_items:
            graphic_item.draw(geo.add_2d(position, (1, 1)))


class EntityStatusList(RectangularUIElement):
    def __init__(self, rect, margin=geo.zero2d(), vertical_space=0):
        super(EntityStatusList, self).__init__(rect, margin=margin)
        self._entity_stack_panel = \
            StackPanelVertical(rect.top_left, (0, 0),
                               vertical_space=vertical_space)
        self._offset = (0, 0)

    def update(self, entity):
        seen_entities = entity.vision.get_seen_entities_closest_first()
        seen_entities.reverse()
        if entity in seen_entities:
            seen_entities.remove(entity)
        self._entity_stack_panel.clear()
        rect = geo.Rect(geo.zero2d(), self.width, 3)
        for seen_entity in seen_entities:
            entity_status = EntityStatus(seen_entity, rect)
            self._entity_stack_panel.append(entity_status)
        self._offset = (0, settings.WINDOW_HEIGHT - self._entity_stack_panel.height - constants.STATUS_BAR_HEIGHT)

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(geo.add_2d(offset, self.margin), self._offset)
        self._entity_stack_panel.draw(position)


class EntityStatus(UIElement):
    def __init__(self, entity, rect, margin=geo.zero2d()):
        super(EntityStatus, self).__init__(margin)
        self._width = rect.width
        element_width = self.width - style.interface_theme.margin[0] * 2 - 2
        monster_health_bar = CounterBar(entity.health.hp, element_width,
                                        colors.HP_BAR_FULL,
                                        colors.HP_BAR_EMPTY)

        entity_symbol = SymbolUIElement((0, 0), entity.graphic_char.symbol,
                                        entity.graphic_char.color_fg)

        self._hp_stack_panel = StackPanelHorizontal((0, 0), (1, 1), 1)
        self._hp_stack_panel.append(entity_symbol)
        self._hp_stack_panel.append(monster_health_bar)

        self._rectangle_bg = \
            StyledRectangle(rect, style.monster_list_card,
                            entity.description.name, entity.graphic_char.color_fg)

        self._status_stack_panel = StackPanelVertical(rect.top_left, margin)
        self._status_stack_panel.append(self._hp_stack_panel)

    @property
    def height(self):
        return self._status_stack_panel.height

    @property
    def width(self):
        return self._width

    def draw(self, offset=geo.zero2d()):
        self._rectangle_bg.draw(offset)
        self._status_stack_panel.draw(offset)


class MessageDisplay(RectangularUIElement):
    def __init__(self, rect, margin=(0, 0), vertical_space=0):
        super(MessageDisplay, self).__init__(rect, margin=margin)
        self._message_stack_panel = \
            StackPanelVertical(rect.top_left,
                               margin=style.interface_theme.margin,
                               vertical_space=vertical_space)
        self._rectangle_bg = \
            StyledRectangle(rect, style.interface_theme.rect_style)

    def update(self):
        messages_height = (self.height -
                           style.interface_theme.margin[0] * 2)
        messages = messenger.tail(messages_height)
        self._message_stack_panel.clear()
        for message in messages:
            if message.turn_created == turn.current_turn - 1:
                color = colors.TEXT_NEW
            else:
                color = colors.TEXT_OLD
            message_width = (self.width -
                             style.interface_theme.margin[0] * 2)
            words = str(message).split()
            lines = []
            line = words[0]
            for word in words[1:]:
                if len(line) + len(" " + word) > message_width:
                    lines.append(line)
                    line = word
                else:
                    line += (" " + word)

            if len(line) >= 1:
                lines.append(line)
            for line in lines:
                text_box = TextBox(str(line).ljust(message_width),
                                   geo.zero2d(), color, geo.zero2d())
                self._message_stack_panel.append(text_box)

    def draw(self, offset=geo.zero2d()):
        self._rectangle_bg.draw(offset)
        self._message_stack_panel.draw(offset)


class CounterBar(UIElement):
    """
    Draws a bar showing the ratio between the current and max value of counter.
    """

    def __init__(self, counter, width, active_color, inactive_color,
                 margin=(0, 0), offset=geo.zero2d()):
        super(CounterBar, self).__init__(margin)
        self.offset = offset
        self.counter = counter
        self.active_color = active_color
        self.inactive_color = inactive_color
        self._width = width

    @property
    def height(self):
        return 1

    @property
    def width(self):
        return self._width

    def _draw_bar(self, offset=geo.zero2d()):
        """
        Draws the bar.
        """
        tiles_active = int(math.ceil(self.counter.ratio_of_full() *
                                     self.width))
        x, y = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        for i in range(tiles_active):
            console.set_symbol((x + i, y), ' ')
            console.set_color_bg((x + i, y), self.active_color)
        for i in range(tiles_active, self.width):
            console.set_symbol((x + i, y), ' ')
            console.set_color_bg((x + i, y), self.inactive_color)

    def draw(self, offset=geo.zero2d()):
        """
        Draws the bar.
        """
        self._draw_bar(offset)


class CounterBarWithNumbers(CounterBar):
    """
    Will display current and max value of counter on the bar.
    """

    def __init__(self, counter, width, active_color, inactive_color,
                 text_color, margin=(0, 0), offset=geo.zero2d()):
        super(CounterBarWithNumbers, self).__init__(counter, width,
                                                    active_color,
                                                    inactive_color,
                                                    margin, offset)
        self.text_color = text_color

    def draw(self, offset=geo.zero2d()):
        """
        Draws the bar with numbers.
        """
        self._draw_bar(offset)
        console.set_default_color_fg(self.text_color)
        self._draw_numbers(offset)

    def _draw_numbers(self, offset):
        """
        Draws the numbers.
        """
        x, y = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        text = (str(self.counter.value) +
                " (" + str(self.counter.max_value) + ")")
        x_offset = (self.width - len(text)) / 2
        position = (x + x_offset, y)

        console.print_text(position, text)


class TextBox(UIElement):
    def __init__(self, text, offset, color_fg, margin=(0, 0)):
        super(TextBox, self).__init__(margin)
        self.offset = offset
        self.text = text
        self.color_fg = color_fg

    @property
    def height(self):
        result = self.text.count('\n') + 1
        return result

    @property
    def width(self):
        lines = self.text.split("\n")
        return max([len(line) for line in lines])

    def draw(self, offset=geo.zero2d()):
        x, y = geo.int_2d(geo.add_2d(geo.add_2d(offset, self.offset),
                                     self.margin))
        if x > settings.WINDOW_WIDTH:
            return
        if x + len(self.text) > settings.WINDOW_WIDTH:
            max_width = settings.WINDOW_WIDTH - x
            show_text = self.text[:max_width - 3] + "..."
        else:
            show_text = self.text

        console.set_default_color_fg(self.color_fg)
        console.print_text((x, y), show_text)


class SymbolUIElement(UIElement):
    def __init__(self, offset, the_symbol, color_fg, color_bg=None, margin=(0, 0)):
        super(SymbolUIElement, self).__init__(margin)
        self.offset = offset
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.symbol = the_symbol

    @property
    def height(self):
        return 1

    @property
    def width(self):
        return 1

    def draw(self, offset=geo.zero2d()):
        x, y = geo.int_2d(geo.add_2d(geo.add_2d(offset, self.offset),
                                     self.margin))
        if not self.color_fg is None:
            console.set_color_fg((x, y), self.color_fg)
        if not self.color_bg is None:
            console.set_color_bg((x, y), self.color_bg)
        console.set_symbol((x, y), self.symbol)
