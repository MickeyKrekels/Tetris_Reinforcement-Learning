import random
import pygame
from pathlib import Path

pygame.font.init()

# global variables

col = 10  # 10 columns
row = 20  # 20 rows
s_width = 800  # window width
s_height = 750  # window height
play_width = 300  # play window width; 300/10 = 30 width per block
play_height = 600  # play window height; 600/20 = 20 height per block
block_size = 30  # size of block

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

filepath = 'highscore.txt'
font_path_arcade = './font/arcade.ttf'
font_path_mario = './font/mario.ttf'

arcade_font = pygame.font.SysFont(font_path_arcade, 30, bold=True)
mario_font = pygame.font.SysFont(font_path_mario, 65, bold=True)

SPEED = 40

# shapes formats

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['.....',
      '..0..',
      '..0..',
      '..0..',
      '..0..'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# index represents the shape
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# class to represent each of the pieces

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]  # choose color from the shape_color list
        self.rotation = 0  # chooses the rotation according to index


class Game:
    def __init__(self, w=s_width, h=s_height):
        self.w = w
        self.h = h
        self.locked_positions = {}
        self.create_grid(self.locked_positions)
        self.clock = pygame.time.Clock()

        self.current_piece = self.get_shape()
        self.next_piece = self.get_shape()

        # flags
        self.change_piece = False 
        self.score = 0
        self.last_score = self.get_max_score()
        self.window = pygame.display.set_mode((s_width, s_height))
        pygame.display.set_caption('Tetris')

# initialise the grid
    def create_grid(self,locked_pos={}):
        grid = [[(0, 0, 0) for x in range(col)] for y in range(row)]  # grid represented rgb tuples

        # locked_positions dictionary
        # (x,y):(r,g,b)
        for y in range(row):
            for x in range(col):
                if (x, y) in locked_pos:
                    color = locked_pos[
                        (x, y)]  # get the value color (r,g,b) from the locked_positions dictionary using key (x,y)
                    grid[y][x] = color  # set grid position to color

        return grid


    def convert_shape_format(self,piece):
        positions = []
        shape_format = piece.shape[piece.rotation % len(piece.shape)]  # get the desired rotated shape from piece

        for i, line in enumerate(shape_format):  # i gives index; line gives string
            row = list(line)  # makes a list of char from string
            for j, column in enumerate(row):  # j gives index of char; column gives char
                if column == '0':
                    positions.append((piece.x + j, piece.y + i))

        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)  # offset according to the input given with dot and zero

        return positions

    # checks if current position of piece in grid is valid
    def valid_space(self,piece, grid):
        # makes a 2D list of all the possible (x,y)
        accepted_pos = [[(x, y) for x in range(col) if grid[y][x] == (0, 0, 0)] for y in range(row)]
        # removes sub lists and puts (x,y) in one list; easier to search
        accepted_pos = [x for item in accepted_pos for x in item]

        formatted_shape = self.convert_shape_format(piece)

        for pos in formatted_shape:
            if pos not in accepted_pos:
                if pos[1] >= 0:
                    return False
        return True

    # check if piece is out of board
    def check_lost(self,positions):
        for pos in positions:
            x, y = pos
            if y < 1:
                return True
        return False

    # chooses a shape randomly from shapes list
    def get_shape(self):
        return Piece(5, 0, random.choice(shapes))

    # draws text in the middle
    def draw_text_middle(self,text, color, surface):
        label = arcade_font.render(text, 1, color)

        surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2)))

    # draws the lines of the grid for the game
    def draw_grid(self,surface):
        r = g = b = 0
        grid_color = (r, g, b)

        for i in range(row):
            # draw grey horizontal lines
            pygame.draw.line(surface, grid_color, (top_left_x, top_left_y + i * block_size),
                             (top_left_x + play_width, top_left_y + i * block_size))
            for j in range(col):
                # draw grey vertical lines
                pygame.draw.line(surface, grid_color, (top_left_x + j * block_size, top_left_y),
                                 (top_left_x + j * block_size, top_left_y + play_height))

    # clear a row when it is filled
    def clear_rows(self,grid, locked):
        # need to check if row is clear then shift every other row above down one
        increment = 0
        for i in range(len(grid) - 1, -1, -1):      # start checking the grid backwards
            grid_row = grid[i]                      # get the last row
            if (0, 0, 0) not in grid_row:           # if there are no empty spaces (i.e. black blocks)
                increment += 1
                # add positions to remove from locked
                index = i                           # row index will be constant
                for j in range(len(grid_row)):
                    try:
                        del locked[(j, i)]          # delete every locked element in the bottom row
                    except ValueError:
                        continue

        # shift every row one step down
        # delete filled bottom row
        # add another empty row on the top
        # move down one step
        if increment > 0:
            # sort the locked list according to y value in (x,y) and then reverse
            # reversed because otherwise the ones on the top will overwrite the lower ones
            for key in sorted(list(locked), key=lambda a: a[1])[::-1]:
                x, y = key
                if y < index:                       # if the y value is above the removed index
                    new_key = (x, y + increment)    # shift position to down
                    locked[new_key] = locked.pop(key)

        return increment

    # draws the upcoming piece
    def draw_next_shape(self,piece, surface):
        label = arcade_font.render('Next shape', 1, (255, 255, 255))

        start_x = top_left_x + play_width + 50
        start_y = top_left_y + (play_height / 2 - 100)

        shape_format = piece.shape[piece.rotation % len(piece.shape)]

        for i, line in enumerate(shape_format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, piece.color, (start_x + j*block_size, start_y + i*block_size, block_size, block_size), 0)

        surface.blit(label, (start_x, start_y - 30))

    # draws the content of the window
    def draw_window(self,surface, grid, score=0, last_score=0):
        surface.fill((0, 0, 0))  # fill the surface with black

        pygame.font.init()  # initialise font
        label = mario_font.render('TETRIS', 1, (255, 255, 255))  # initialise 'Tetris' text with white

        surface.blit(label, ((top_left_x + play_width / 2) - (label.get_width() / 2), 30))  # put surface on the center of the window

        # current score
        label = arcade_font.render('SCORE   ' + str(score) , 1, (255, 255, 255))

        start_x = top_left_x + play_width + 50
        start_y = top_left_y + (play_height / 2 - 100)

        surface.blit(label, (start_x, start_y + 200))

        # last score
        label_hi = arcade_font.render('HIGHSCORE   ' + str(last_score), 1, (255, 255, 255))

        start_x_hi = top_left_x - 240
        start_y_hi = top_left_y + 200

        surface.blit(label_hi, (start_x_hi + 20, start_y_hi + 200))

        # draw content of the grid
        for i in range(row):
            for j in range(col):
                # pygame.draw.rect()
                # draw a rectangle shape
                # rect(Surface, color, Rect, width=0) -> Rect
                pygame.draw.rect(surface, grid[i][j],
                                 (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

        # draw vertical and horizontal grid lines
        self.draw_grid(surface)

        # draw rectangular border around play area
        border_color = (255, 255, 255)
        pygame.draw.rect(surface, border_color, (top_left_x, top_left_y, play_width, play_height), 4)

    # update the score txt file with high score
    def update_score(self,new_score):
        score = self.get_max_score()

        # will create file, if it exists will do nothing
        filename = Path(filepath)
        filename.touch(exist_ok=True)  

        with open(filepath, 'w') as file:
            if new_score > score:
                file.write(str(new_score))
            else:
                file.write(str(score))

    # get the high score from the file
    def get_max_score(self):
        filename = Path(filepath)
        filename.touch(exist_ok=True)  

        with open(filepath, 'r') as file:
            lines = file.readlines()        # reads all the lines and puts in a list
            score = int(lines[0].strip())   # remove \n

        return score

    def step_agent(self):
        grid = self.create_grid(self.locked_positions)
        self.clock.tick(SPEED)

        return

    def step_player(self):
        self.grid = self.create_grid(self.locked_positions)
        self.clock.tick(SPEED)

        for event in pygame.event.get(): # gets player input
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.current_piece.x -= 1  # move x position left
                    if not self.valid_space(self.current_piece, self.grid):
                        self.current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    self.current_piece.x += 1  # move x position right
                    if not self.valid_space(self.current_piece, self.grid):
                        self.current_piece.x -= 1

                elif event.key == pygame.K_UP:
                    # rotate shape
                    self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
                    if not self.valid_space(self.current_piece, self.grid):
                        self.current_piece.rotation = self.current_piece.rotation - 1 % len(self.current_piece.shape)

        piece_pos = self.convert_shape_format(self.current_piece)

        self.current_piece.y += 1
        if not self.valid_space(self.current_piece, self.grid) and self.current_piece.y > 0:
            self.current_piece.y -= 1
            self.change_piece = True

        # draw the piece on the grid by giving color in the piece locations
        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y >= 0:
                self.grid[y][x] = self.current_piece.color

        if self.change_piece:  # if the piece is locked
            for pos in piece_pos:
                p = (pos[0], pos[1])
                self.locked_positions[p] = self.current_piece.color       # add the key and value in the dictionary
            self.current_piece = self.next_piece
            self.next_piece = self.get_shape()
            self.change_piece = False
            self.score += self.clear_rows(self.grid, self.locked_positions) * 10    # increment score by 10 for every row cleared
            self.update_score(self.score)

            if self.last_score < self.score:
                self.last_score = self.score

        self.draw_window(self.window, self.grid, self.score, self.last_score)
        self.draw_next_shape(self.next_piece, self.window)
        pygame.display.update()

        game_over = False

        if self.check_lost(self.locked_positions):
            print("Game over")
            game_over = True      

        return game_over , self.score


def main():
    game = Game()


    while True:
        gameover, score = game.step_player()

        if gameover:
            break

    pygame.time.delay(2000)  # wait for 2 seconds
    pygame.quit()


if __name__ == '__main__':
    main()  # start game
