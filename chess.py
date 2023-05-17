import pygame, sys, math
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
    return (coordinate[0], 8 * 62 - coordinate[1])

class Tile:
    def __init__(self, color, position, size):
        self.color = color
        self.position = position
        self.size = size
        self.color_copy = color

        self.rect = pygame.Rect(self.position[0], self.position[1], self.size, self.size)

    def draw(self):
        pygame.draw.rect(window, self.color, self.rect)

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

def inside(set):
    moves = []
    for move in list(set):
        if move[0] < 8 and move[0] >= 0:
           if move[1] < 8 and move[1] >= 0:
                moves.append(move)

    return moves

def valid_moves(piece, board):
    moves_set = set()
    piece_type = piece.piece
    position = (piece.position[0] // 62 - 2, piece.position[1] // 62)
    color = piece.color

    if piece_type == 'pawn': 
        if color == 'black':
            return [(position[0], position[1] - 1)]
        elif color == 'white':
            return [(position[0], position[1] + 1)]
        
    if piece_type == 'rook':
        for y in range(8):
            for x in range(8):
                moves_set.add((position[0], position[1] + y))
                moves_set.add((position[0] - x, position[1]))
                moves_set.add((position[0], position[1] - y))
                moves_set.add((position[0] + x, position[1]))
    
    if piece_type == 'bishop':
        for y in range(8):
            moves_set.add((position[0] + y, position[1] + y))
            moves_set.add((position[0] - y, position[1] - y))
            moves_set.add((position[0] + y, position[1] - y))
            moves_set.add((position[0] - y, position[1] + y))
    
    if piece_type == 'knight':
        moves_set.add((position[0] + 2, position[1] - 1))
        moves_set.add((position[0] + 2, position[1] + 1))
        moves_set.add((position[0] + 1, position[1] + 2))
        moves_set.add((position[0] - 1, position[1] + 2))
        moves_set.add((position[0] - 2, position[1] + 1))
        moves_set.add((position[0] - 2, position[1] - 1))
        moves_set.add((position[0] - 1, position[1] - 2))
        moves_set.add((position[0] + 1, position[1] - 2))
    
    if piece_type == 'king':
        moves_set.add((position[0] + 1, position[1] - 1))
        moves_set.add((position[0] + 1, position[1] + 1))
        moves_set.add((position[0] - 1, position[1] + 1))
        moves_set.add((position[0] - 1, position[1] - 1))
        moves_set.add((position[0] + 1, position[1] - 1))
        moves_set.add((position[0] - 1, position[1] - 1))
        moves_set.add((position[0] - 1, position[1] - 1))
        moves_set.add((position[0] + 1, position[1] + 1))
        moves_set.add((position[0] - 1, position[1]))
        moves_set.add((position[0] + 1, position[1]))
        moves_set.add((position[0], position[1] + 1))
        moves_set.add((position[0], position[1] - 1))
    
    if piece_type == 'queen':
        for y in range(8):
            for x in range(8):
                moves_set.add((position[0] + y, position[1]))
                moves_set.add((position[0], position[1] - x))
                moves_set.add((position[0] - y, position[1]))
                moves_set.add((position[0], position[1] + x))

        for y in range(8):
            moves_set.add((position[0] + y, position[1] + y))
            moves_set.add((position[0] - y, position[1] - y))
            moves_set.add((position[0] + y, position[1] - y))
            moves_set.add((position[0] - y, position[1] + y))

    moves = inside(moves_set)
    
    for square in moves:
        if board[square]['occupied'] == True or board[square]['piece'] != None and square in moves:
            moves.remove(square)

    return moves

class Chessboard:
    def __init__(self):
        self.map = Tilemap(WIDTH / 2, [(118,150,86), (238,238,210)])
        self.positions = {}
        self.board_state = {}
        self.selected = None

        self.coordinates = []
        for x in range(8):
            for y in range(8):
                self.coordinates.append((y, x))

        for tile, coord in zip(self.map.tiles, self.coordinates):
            self.positions[f'{coord}'] = tile.rect.center
            self.board_state[coord] = {'occupied': False, 
                                        'piece': None, 
                                        'center': tile.rect.center, 
                                        'rect': tile.rect,
                                        'tile': tile,
                                        'original_color': tile.color}

        self.pieces = []
        self.order = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook']
        for piece, position in zip(self.order, list(self.positions.values())[:8]):
            self.pieces.append(Piece('white', piece, position))

        for piece, position in zip(self.order, list(self.positions.values())[-8:]):
            self.pieces.append(Piece('black', piece, position))

        for position in list(self.positions.values())[-16:-8]:
            self.pieces.append(Piece('black', 'pawn', position))

        for position in list(self.positions.values())[8:16]:
            self.pieces.append(Piece('white', 'pawn', position))

        self.colors = ['white', 'black']
        self.movements = ['black']

    def controller(self):

        for piece in self.pieces:
            if pygame.mouse.get_pressed()[0] and piece.rect.collidepoint(pygame.mouse.get_pos()):
                if piece.color != self.movements[-1]:
                    self.selected = piece
                
        for element in self.board_state:
            self.board_state[element]['occupied'] = False

        for piece in self.pieces:
            for element in self.board_state:

                if self.board_state[element]['rect'].colliderect(piece.rect):
                    self.board_state[element]['occupied'] = True
                
                if self.board_state[element]['occupied'] == True:
                    self.board_state[element]['piece'] = piece.piece
                    self.board_state[element]['tile'].color = (255, 0, 0)
                else:
                    self.board_state[element]['piece'] = None
                    self.board_state[element]['tile'].color = self.board_state[element]['original_color']
                    
                if piece == self.selected:
                    if element in valid_moves(piece, self.board_state):
                        pygame.draw.circle(window, (80, 80, 80), self.board_state[element]['center'], 8)
                        if pygame.mouse.get_pressed()[0] and self.board_state[element]['rect'].collidepoint(pygame.mouse.get_pos()):
                            piece.position = self.board_state[element]['center']
                            self.movements.append(piece.color)
                            self.selected = None

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
        keys = pygame.key.get_pressed()
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