import pygame as pg
from math import floor
pg.init()


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

GRID_SIZE = 15
"""number of tiles per tile and column"""

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 600
TILE_SIZE = WINDOW_HEIGHT/GRID_SIZE
LINE_WINDOW_WIDTH = 1

DIRECTIONS = ((1,0),(0,1),(1,1),(-1,1))

MAX_RECURSIONS = 2
"""maximal depth of recursion of the minimax algorithm"""
TARGET_LEN = 5
"""number of symbols in a row needed to win the game"""          


game = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]
"""two-dimensional list representing the grid; empty tile is represented by None, X by False and O by True"""
player_turn = False
"""X's turn is represented by False, O's Turn by False, end of the game by None"""
turn_number = 0
"""number of turns that have been played"""




def initiate_game_window():
    window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pg.display.set_caption("Five in a row")
    window.fill(WHITE)
    for i in range(1,GRID_SIZE):
        pg.draw.line(window, BLACK, (WINDOW_WIDTH / GRID_SIZE*i, 0), (WINDOW_WIDTH / GRID_SIZE*i, WINDOW_HEIGHT), LINE_WINDOW_WIDTH)
        pg.draw.line(window, BLACK, (0, WINDOW_HEIGHT / GRID_SIZE*i), (WINDOW_WIDTH, WINDOW_HEIGHT / GRID_SIZE*i), LINE_WINDOW_WIDTH)
    return window

def user_click():
    """
    Determins player's turn from the position of mouse and changes
    corresponding element in the list representing game, returns this position
    in the grid as a tuple, changes variables describing turn to next turn.
    """
    global player_turn, turn_number, game
    x,y = pg.mouse.get_pos()
    col = floor(x/TILE_SIZE)
    row = floor(y/TILE_SIZE)
    if game[row][col] == None:
        game[row][col] = player_turn
        player_turn = not player_turn
        turn_number += 1
    return (row,col)

def update_grid(game):
    """
    Redraws the grid in game window according to current state of game.
    Draws white background and grid, then iterates through every tile and if
    there is X (or O) in the current game state draws X (or O) into the
    coresponding tile in the drawn grid. 
    """
    window.fill(WHITE)
    for i in range(1,GRID_SIZE):
        pg.draw.line(window, BLACK, (WINDOW_WIDTH / GRID_SIZE*i, 0), (WINDOW_WIDTH / GRID_SIZE*i, WINDOW_HEIGHT), LINE_WINDOW_WIDTH)
        pg.draw.line(window, BLACK, (0, WINDOW_HEIGHT / GRID_SIZE*i), (WINDOW_WIDTH, WINDOW_HEIGHT / GRID_SIZE*i), LINE_WINDOW_WIDTH)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if game[row][col] == None: continue
            elif game[row][col]:
                pg.draw.circle(window, BLUE, ((col+0.5)*TILE_SIZE+1, (row+0.5)*TILE_SIZE+1), TILE_SIZE*0.45, LINE_WINDOW_WIDTH)
            else:
                pg.draw.line(window, RED, ((col+0.1)*TILE_SIZE, (row+0.1)*TILE_SIZE), ((col+0.9)*TILE_SIZE, (row+0.9)*TILE_SIZE), LINE_WINDOW_WIDTH)
                pg.draw.line(window, RED, ((col+0.1)*TILE_SIZE, (row+0.9)*TILE_SIZE), ((col+0.9)*TILE_SIZE, (row+0.1)*TILE_SIZE), LINE_WINDOW_WIDTH)

def announce_winner(winner):
    """
    Creates a surface with a text in corresponding color stating win or lose for the player.
    """
    font = pg.font.Font(None, 50)
    if winner is None: text = font.render("DRAW", True, BLACK)
    elif winner: text = font.render("YOU LOSE", True, BLUE)
    else: text = font.render("YOU WIN", True, RED)
    text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
    window.blit(text, text_rect)

def evaluate_game(game):
    """
    static evaluation of a game state; for every continuouse
    [goal number of symbols]-tuple containing only Xs (or Os) subtracts
    (or adds) the cube of number of Xs (or Os) in the tuple
    """
    score = 0
    for i in range(GRID_SIZE):
        score += evaluate_tuple(game[i])                                                        #rows
        score += evaluate_tuple(tuple(game[j][i] for j in range(GRID_SIZE)))                    #columns
    score += evaluate_tuple(tuple(game[j][j] for j in range(GRID_SIZE)))                        #main \diagonal
    score += evaluate_tuple(tuple(game[j][GRID_SIZE-j-1] for j in range(GRID_SIZE)))            #main /diagonal
    for i in range(1,GRID_SIZE-TARGET_LEN+1):
        score += evaluate_tuple(tuple(game[j][i+j] for j in range(GRID_SIZE-i)))                #\diagonals
        score += evaluate_tuple(tuple(game[i+j][j] for j in range(GRID_SIZE-i)))
        score += evaluate_tuple(tuple(game[GRID_SIZE-1-i-j][j] for j in range(GRID_SIZE-i)))    #/diagonals
        score += evaluate_tuple(tuple(game[GRID_SIZE-1-j][i+j] for j in range(GRID_SIZE-i)))
    return score

def evaluate_tuple(line):
    """
    returns cube of number of Xs (or Os) in the tuple if there are only Xs
    (or Os); otherwise returns 0
    """
    score = 0
    tuple_x = 0
    tuple_o = 0
    for i in range(TARGET_LEN):
        if line[i] == True: tuple_o += 1
        if line[i] == False: tuple_x += 1
    if tuple_x==0: score += tuple_o**3
    elif tuple_o==0: score -= tuple_x**3
    for i in range(TARGET_LEN, len(line)):
        if line[i] == True: tuple_o += 1
        elif line[i] == False: tuple_x += 1
        if line[i-TARGET_LEN] == True: tuple_o -= 1
        if line[i-TARGET_LEN] == False: tuple_x -= 1
        if tuple_x==0: score += tuple_o**3
        elif tuple_o==0: score -= tuple_x**3
    return score

def game_end(game, last_move):
    """
    Checks if one of there is a new winning sequence of symbols in the game.
    Determins last player from the last move position in game and for all four
    orientations counts number of symbols in uninterrupted tuple in both
    directions from the last move. If there is a winning tuple, the function
    returns the winner; otherwise it returns None
    """
    (row, col) = last_move
    player = game[row][col]
    for (drow, dcol) in DIRECTIONS:
        n = 1
        i = 1
        while in_grid(row+i*drow,col+i*dcol) and game[row+i*drow][col+i*dcol] == player:
            n += 1
            i += 1
        i = 1
        while in_grid(row-i*drow,col-i*dcol) and game[row-i*drow][col-i*dcol] == player:
            n += 1
            i += 1
        if n >= TARGET_LEN: return player
        
    return None       
    
def in_grid(row,col):
    """Returns True if the position is inside game grid; otherwise returns False."""
    if row<0 or col<0 or row>=GRID_SIZE or col>=GRID_SIZE: return False
    return True

def order(game):
    """
    Returns list of possible moves that are not further than
    [goal length of tuple]-1 from an already placed symbol ordered from the
    nearest to the furthest. Creates 2d list (for distances forom closest
    placed symbol) with Nones for empty tiles and 0s for Xs and Os then
    multiple times iterates through every element of distance and on n-th
    iteration places n to every tile containing None next to tile containing
    n-1 and adds the position to the list that is returned at the end.
    """
    ordered_list = []
    distance = [[None if game[i][j] == None else 0 for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]
    for d in range(TARGET_LEN-1):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if distance[i][j] == d:
                    for (di,dj) in DIRECTIONS:
                        if (in_grid(i+di,j+dj) and distance[i+di][j+dj] == None):
                            ordered_list.append((i+di,j+dj))
                            distance[i+di][j+dj] = d+1
                        if (in_grid(i-di,j-dj) and distance[i-di][j-dj] == None):
                            ordered_list.append((i-di,j-dj))
                            distance[i-di][j-dj] = d+1

    return ordered_list
    

def minimax(turn_number, depth, game, player_turn, alternative_value, last_move = None):
    """
    an implementation of the minimax algorithm with alpha-beta pruning
    if the algorithm gets to a leaf where one of the players wins, the it
    assigns this state a value which is a sum of a constant and a static
    evaluation. The constant is positive if the winner is X and negative if O
    and its absolute value is always grater than the static evaluation, so the
    value assigned to the state is always greater (or lesser) than evaluation
    of any other state, but different winning and losing states can still be
    compared with each other. If the algorythm gets to the maximum depth of
    recursion it evaluates the game state.
    """
    if not last_move == None and not (winner := game_end(game,last_move)) is None:
        return ((1 if winner else -1)*(GRID_SIZE**2)*(TARGET_LEN**3) + evaluate_game(game),)
    
    if turn_number >= GRID_SIZE**2:
        return (0,)
    
    if depth == MAX_RECURSIONS:
        return (evaluate_game(game),)
    
    if player_turn: best_move = (float('-inf'),)
    else: best_move = (float('inf'),)
    for (row,col) in order(game):
        game[row][col] = player_turn
        move = minimax(turn_number+1, depth+1, game, not player_turn, best_move[0], (row,col))
        game[row][col] = None
        if (player_turn == (alternative_value < move[0])) or (alternative_value == move[0]): return move
        if player_turn == (best_move[0] < move[0]) and best_move[0] != move[0]: best_move = (move[0], row, col)
                    
    return best_move




window = initiate_game_window()
run = True
last_move = None

while run:
    if player_turn == True:    
        if player_turn: alt_val = float('inf')
        else: alt_val = float('-inf')
        move = minimax(turn_number, 0, game, player_turn, alt_val)
        game[move[1]][move[2]] = player_turn
        turn_number += 1
        player_turn = not player_turn
        last_move=(move[1],move[2])
    else:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if player_turn == False:
                    last_move = user_click()
    
    update_grid(game)
    if last_move != None and (winner := game_end(game,last_move)) != None:
        announce_winner(winner)
        player_turn = None
    elif turn_number >=GRID_SIZE**2:
        announce_winner(None)
        player_turn = None
    pg.display.update()
    


pg.quit()
