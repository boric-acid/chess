import pygame, sys, time
from random import randint
from os.path import abspath, join, splitext, basename
from os import listdir

pygame.init()
size = 62
WIDTH, HEIGHT = 800, size * 8
window = pygame.display.set_mode((WIDTH, HEIGHT))

title = pygame.display.set_caption('Platformer')
clock, FPS = pygame.time.Clock(), 60

def write(text, size, position:tuple, color, centered:pygame.Rect or bool = None):
    font = pygame.font.SysFont('segoeuisemibold', size)
    text = font.render(text, True, color)
    if centered:
        text_rect = text.get_rect()
        if isinstance(centered, pygame.Rect):
            text_rect.center = centered.center
        elif centered == True:
            text_rect.center = position
        window.blit(text, text_rect)
    else:
        window.blit(text, position)

def pieces():
    dir_path = r'C:\Users\horac\OneDrive\Escritorio\Python\pygame\pieces'
    images = [join(dir_path, image) for image in listdir(dir_path)]

    pieces = {}

    for image in images:
        if str(splitext(image)[0][-1]).isnumeric():
            pieces[f'black_{splitext(basename(image))[0][0:-1]}'] = pygame.image.load(image)
        else:
            pieces[f'white_{splitext(basename(image))[0]}'] = pygame.image.load(image)

    return pieces

def opposite(coordinate: tuple):
    return (coordinate[0], 7 - coordinate[1])

class Tile:
    def __init__(self, color: tuple or pygame.Surface, position, size):
        self.color = color
        self.tuple, self.image = False, False

        if isinstance(self.color, tuple):
            self.tuple = True
        elif isinstance(self.color, pygame.Surface):
            self.image = True
            self.color = pygame.transform.scale(self.color, (size, size))

        self.position = position
        self.size = size

        self.rect = pygame.Rect(self.position[0], self.position[1], self.size, self.size)

    def draw(self):
        if self.tuple:
            pygame.draw.rect(window, self.color, self.rect)
        elif self.image:
            window.blit(self.color, self.position)

class Tilemap:
    def __init__(self, center, colors):
        self.center = center
        self.colors = colors
        self.tiles = []

        for x in range(8):
            for y in range(8):
                self.tiles.append(Tile(self.colors[(x + y) % 2], (self.center - (62 * 4) + y * 62, x * 62), 62))

        self.entire_map = pygame.Rect(self.tiles[0].rect.x, self.tiles[0].rect.y, 62 * 8, 62 * 8)            

    def draw(self):
        for tile in self.tiles:
            tile.draw()

class Piece:
    def __init__(self, color, piece, position):
        self.color = color
        self.piece = piece

        images = pieces()
        self.image = images[f'{self.color}_{self.piece}']
        self.normal = images[f'{self.color}_{self.piece}']
        self.focus = pygame.transform.scale(self.image, (45, 45))
        self.width = self.image.get_width()
        self.half = self.image.get_width() / 2
        self.position = position
        self.selected = False

        self.rect = pygame.Rect(self.position[0] - self.half, self.position[1] - self.half, self.width, self.width)

    def draw(self):
        self.half = self.image.get_width() / 2

        self.rect = pygame.Rect(self.position[0] - self.half, self.position[1] - self.half, self.width, self.width)
        window.blit(self.image, (self.position[0] - self.half, self.position[1] - self.half))    

def inside(position):
    types = [set, list]

    if type(position) in types:
        moves = []
        for move in list(position):
            if move[0] in range(8) and move[1] in range(8):
                moves.append(move)

        return moves
    elif type(position) == tuple:
        return (position[0] in range(8) and position[1] in range(8))

def to_coord(real_position):
    return (real_position[0] // 62 - 2, real_position[1] // 62)

def validate(piece, board, colored):
    moves_set = set()
    eatable = set()
    piece_type = piece.piece
    position = to_coord(piece.position)
    color = piece.color

    colored[position] = None

    def valid(coord):
        invalid = [None, color]
        return (colored[coord] not in invalid)
    
    def bishop_moves(position, board, set):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        nw, sw, ne, se = [], [], [], []
        all = [nw, sw, ne, se]

        nw1, sw1, ne1, se1 = [], [], [], []
        eat = [nw1, sw1, ne1, se1]

        for idx, dir in enumerate(directions):
            x, y = dir
            for i in range(8):
                pos = (position[0] + (x * i), position[1] + (y * i))
                if pos != position:
                    eat[idx].append(pos)

                if pos in board:
                    if pos != position:
                        all[idx].append(i)
                else:
                    if pos[0] in range(0, 8) and pos[1] in range(0, 8):
                        all[idx].append(pos)

        for lista in eat:
            for pos in lista:
                if pos in board:
                    if valid(pos):
                        eatable.add(pos)
                    break

        [l.remove(position) for l in all if position in l]

        limited, unlimited = [], []
        for l in all:
            for pos in l:
                if isinstance(pos, int):
                    limited.append(l[:pos - 1])
                    break
            else:
                unlimited.append(l)
                    
        for lista in [limited, unlimited]:
            for lis in lista:
                for pos in lis:
                    set.add(pos)

    def rook_moves(position, board, set):
        horizontal = []
        vertical = []

        for i in range(8):
            horizontal.append((i, position[1]))
            vertical.append((position[0], i))

        [l.remove(position) for l in [vertical, horizontal] if position in l]

        up, down = [0], [7]
        for i, pos in enumerate(vertical):
            if pos in board:
                if pos[1] < position[1]:
                    up.append(i)
                else:
                    down.append(i)
                
        try:
            moveable = vertical[up[-1]:down[1]]
        except IndexError:
            moveable = vertical[up[-1]:down[0]]

        left, right = [0], [7]
        for i, pos in enumerate(horizontal):
            if pos in board:
                if pos[0] < position[0]:
                    left.append(i)
                else:
                    right.append(i)

        left_pos, right_pos, up_pos, down_pos = [], [], [], []
        for lista in [horizontal, vertical]:
            for pos in lista:
                if pos[0] < position[0]:
                    left_pos.append(pos)
                elif pos[0] > position[0]:
                    right_pos.append(pos)

                if pos[1] < position[1]:
                    up_pos.append(pos)
                elif pos[1] > position[1]:
                    down_pos.append(pos)

        for move in [left_pos[::-1], right_pos, up_pos[::-1], down_pos]:
            for pos in move:
                if pos in board:
                    if valid(pos):
                        eatable.add(pos)
                    break

        try:
            [moveable.append(element) for element in horizontal[left[-1]:right[1]]]
        except IndexError:
            [moveable.append(element) for element in horizontal[left[-1]:right[0]]]

        [set.add(pos) for pos in moveable]

    if piece_type == 'pawn':
        if color == 'black':
            up = -1
            start_row = 6
        else:
            up = 1
            start_row = 1

        if position[1] == start_row and (position[0], position[1] + up) not in board:
            moves_set.add((position[0], position[1] + up))
            moves_set.add((position[0], position[1] + (2*up)))

        if (position[0], position[1] + up) not in board:
            moves_set.add((position[0], position[1] + up))

        possible = [(position[0] + 1, position[1] + up), (position[0] - 1, position[1] + up)]
        for coord in possible:
            if coord in board and valid(coord):
                eatable.add(coord)
        
    if piece_type == 'rook':
        rook_moves(position, board, moves_set)

    if piece_type == 'bishop':
        bishop_moves(position, board, moves_set)

    if piece_type == 'knight':
        directions = [(2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2)]
        for dir in directions:
            pos = (position[0] + dir[0], position[1] + dir[1])
            if inside(pos):
                moves_set.add(pos)
                if valid(pos):
                    eatable.add(pos)
    
    if piece_type == 'king':
        directions = [(1, -1), (1, 1), (-1, 1), (-1, -1), (-1, 0), (1, 0), (0, 1), (0, -1)]
        for dir in directions:
            pos = (position[0] + dir[0], position[1] + dir[1])
            if inside(pos):
                moves_set.add(pos)
                if valid(pos):
                    eatable.add(pos)
    
    if piece_type == 'queen':
        bishop_moves(position, board, moves_set)
        rook_moves(position, board, moves_set)
    
    for square in list(moves_set):
        if square in board:
            moves_set.remove(square)

    if position in moves_set:
        moves_set.remove(position)

    return [inside(moves_set), eatable]

def clicked(rect):
    return (pygame.mouse.get_pressed()[0] and rect.collidepoint(pygame.mouse.get_pos()))

class Chessboard:
    def __init__(self):
        self.primary = [(118,150,86), (238,238,210)]
        self.gray = [(30, 30, 30), (240, 240, 240)]
        self.images = [pygame.image.load(r'C:\Users\horac\OneDrive\Escritorio\Python\pygame\sof_crazy.jpeg'), pygame.image.load(r'C:\Users\horac\OneDrive\Escritorio\Python\pygame\sof_cute.jpeg')]
        self.map = Tilemap(WIDTH / 2, self.primary)
        self.positions = {}
        self.board = {}
        self.selected = None

        self.coordinates = []
        for x in range(8):
            for y in range(8):
                self.coordinates.append((y, x))

        for tile, coord in zip(self.map.tiles, self.coordinates):
            self.positions[f'{coord}'] = tile.rect.center
            self.board[coord] = { 'center': tile.rect.center, 
                                        'rect': tile.rect,
                                        'tile': tile}

        self.pieces = []
        self.order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for piece, position in zip(self.order, list(self.positions.values())[:8]):
            self.pieces.append(Piece('white', piece, position))

        for position in list(self.positions.values())[8:16]:
            self.pieces.append(Piece('white', 'pawn', position))

        for position in list(self.positions.values())[-16:-8]:
            self.pieces.append(Piece('black', 'pawn', position))

        for piece, position in zip(self.order, list(self.positions.values())[-8:]):
            self.pieces.append(Piece('black', piece, position))

        self.colors = ['white', 'black']
        self.movements = ['black']
        self.occupied = [to_coord(piece.position) for piece in self.pieces]

        self.colored = {}
        for coord in self.coordinates:
            if coord[1] < 3:
                self.colored[coord] = 'white'
            elif coord[1] > 5:
                self.colored[coord] = 'black'
            else:
                self.colored[coord] = None

        self.check = False

    def find_piece(self, coord, color):
        for piece in self.pieces:
            if to_coord(piece.position) == coord and piece.color != color:
                return piece
            
    def castling(self, color, type):

        cast = {}
        cast['short'] = [(5, 0), (6, 0)]      
        cast['long'] = [(1, 0), (2, 0), (3, 0)]
        
        if color == 'black':
            cast['long'] = [opposite(coord) for coord in cast['long']]
            cast['short'] = [opposite(coord) for coord in cast['short']]

        for pos in cast[type]:
            if pos in self.occupied:
                free = False
                break
        else:
            free = True

        if free:
            for move in [move[1] for move in self.movements]:
                if move == f'{color}_rook' or move == f'{color}_king':
                    return False
            else:
                return True
        else:
            return False
        
    def consequences(self, piece, element):
        self.occupied.remove(to_coord(piece.position))
        self.colored[element] = piece.color
        piece.position = self.board[element]['center']
        self.movements.append([piece.color, f'{piece.color}_{piece.piece}'])
        self.selected = None
        self.occupied.append(to_coord(piece.position))

    def find_position(self, type, color):
        for piece in self.pieces:
            if piece.piece == type and piece.color != color:
                return to_coord(piece.position)
        else:
            return False #The piece doesn't exist

    def controller(self):

        #self.check = False

        for piece in self.pieces:
            if pygame.mouse.get_pressed()[0] and piece.rect.collidepoint(pygame.mouse.get_pos()):
                if piece.color != self.movements[-1][0]:
                    self.selected = piece

        king = self.find_position('king', piece.color)
        if self.check:
            pygame.draw.circle(window, (255, 0, 0), self.board[king]['center'], 8)

        for element in self.board:
            for piece in self.pieces:
                    
                if piece == self.selected:
                    valid = validate(piece, self.occupied, self.colored)

                    if king in valid[1]:
                        valid[1].remove(king)
                        pygame.draw.circle(window, (255, 0, 0), self.board[king]['center'], 8)
                        self.check = True

                    if element in valid[0]:
                        pygame.draw.circle(window, (80, 80, 80), self.board[element]['center'], 8)
                        if clicked(self.board[element]['rect']):
                            self.consequences(piece, element)
                            print(self.check)
                    elif element in valid[1]:
                        pygame.draw.circle(window, (0, 0, 0), self.board[element]['center'], 8)
                        if clicked(self.board[element]['rect']):
                            self.consequences(piece, element)
                            self.pieces.remove(self.find_piece(element, piece.color))

            if piece == self.selected:
                piece.image = piece.focus
            else:
                piece.image = piece.normal

    def draw(self):
        self.map.draw()

        for piece in self.pieces:
            piece.draw()
            
def main():
    chessboard = Chessboard()

    while True:
        clock.tick(FPS)
        window.fill((20, 20, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit('\u001b[32;1mSuccesfully left the game\u001b[0m')  
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit('\u001b[32;1mSuccesfully left the game\u001b[0m')
        
        write(f'FPS: {round(clock.get_fps())}', 16, (20, 20), (255, 255, 255))    
        chessboard.draw()
        chessboard.controller()

        pygame.display.update()

if __name__ == '__main__':
    main()
