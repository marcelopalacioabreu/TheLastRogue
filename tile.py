from graphic import CharPrinter
from stats import GamePieceType
import compositecore
import frame
import terrain


class Tile(object):
    def __init__(self):
        self.game_pieces = {
            GamePieceType.ENTITY: [],
            GamePieceType.CLOUD: [],
            GamePieceType.ITEM: [],
            GamePieceType.DUNGEON_FEATURE: [],
            GamePieceType.DUNGEON_TRASH: [],
            GamePieceType.TERRAIN: []
        }
        self._top_level = GamePieceType.TERRAIN

    def draw(self, screen_position, is_seen):
        piece_list = self.game_pieces[self._top_level]
        if(is_seen):
            self._draw_seen(screen_position, piece_list)
        else:
            self._draw_unseen(screen_position, piece_list)

    def _update_top_level(self):
        try:
            piece_type = next(pice_type for pice_type in
                              self.game_pieces.keys()
                              if self.has_piece_of_type(pice_type))
            self._top_level = piece_type
        except StopIteration:
            self._top_level = GamePieceType.TERRAIN

    def _cycle_through_pieces(self, piece_list):
        """
        If multiple pieces of the same type share tile.
        create a cycle through each one of them.
        """
        number_of_pieces = len(piece_list)
        if (number_of_pieces > 0):
            animation_length = 3
            cycle_length = number_of_pieces * animation_length
            current_animation_frame = frame.current_frame % cycle_length
            return piece_list[int(current_animation_frame / animation_length)]
        return piece_list[0]

    def add(self, piece):
        piece_type = piece.game_piece_type.value
        self.game_pieces[piece_type].append(piece)
        self._update_top_level()

    def remove(self, piece):
        piece_type = piece.game_piece_type.value
        if(piece in self.game_pieces[piece_type]):
            self.game_pieces[piece_type].remove(piece)
            self._update_top_level()
            return True
        return False

    def _draw_seen(self, screen_position, piece_list):
        piece = self._cycle_through_pieces(piece_list)
        if(piece.graphic_char.color_bg is None):
            self.get_terrain().char_printer.draw(screen_position)
        piece.char_printer.draw(screen_position)

    def _draw_unseen(self, screen_position, piece_list):
        piece_list[0].char_printer.draw_unseen(screen_position)

    def get_first_item(self):
        return self.get_first_piece_of_type(GamePieceType.ITEM)

    def get_first_entity(self):
        return self.get_first_piece_of_type(GamePieceType.ENTITY)

    def get_first_cloud(self):
        return self.get_first_piece_of_type(GamePieceType.CLOUD)

    def get_entities(self):
        return self.game_pieces[GamePieceType.ENTITY]

    def get_terrain(self):
        return self.get_first_piece_of_type(GamePieceType.TERRAIN)

    def get_dungeon_feature(self):
        return self.\
            get_first_piece_of_type(GamePieceType.DUNGEON_FEATURE)

    def get_all_pieces(self):
        return [piece for piece_list in self.game_pieces.values()
                for piece in piece_list]

    def get_first_piece_of_type(self, piece_type):
        if(len(self.game_pieces[piece_type]) < 1):
            return None
        return self.game_pieces[piece_type][0]

    def has_entity(self):
        return self.has_piece_of_type(GamePieceType.ENTITY)

    def has_piece_of_type(self, piece_type):
        if(len(self.game_pieces[piece_type]) < 1):
            return False
        return True

    def copy(self):
        copy = Tile()
        copy.game_pieces = dict()
        for piece_type, piece_list in self.game_pieces.items():
            copy_list = []
            for piece in piece_list:
                new_piece = compositecore.Composite()
                if(piece.has_child("game_piece_type")):
                    new_piece.add_child(piece.game_piece_type.copy())
                if(piece.has_child("graphic_char")):
                    new_piece.add_child(piece.graphic_char.copy())
                if(piece.has_child("description")):
                    new_piece.add_child(piece.description.copy())
                new_piece.add_child(CharPrinter())
                copy_list.append(new_piece)
            copy.game_pieces[piece_type] = copy_list
        return copy


unknown_tile = Tile()
unknown_tile.add(terrain.Unknown())
