import pygame
from copy import deepcopy
from random import choice, randrange

W, H = 10, 20
Tile = 45
game_res = W * Tile, H * Tile
res = 750, 940
FPS = 60

pygame.init()
sc = pygame.display.set_mode(res)
game_sc = pygame.Surface(game_res)
clock = pygame.time.Clock()

grid = [pygame.Rect(x * Tile, y * Tile, Tile, Tile) for x in range(W) for y in range(H)]

figures_position = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                [(0, 0), (0, -1), (0, 1), (-1, -1)],
                [(0, 0), (0, -1), (0, 1), (1, -1)],
                [(0, 0), (0, -1), (0, 1), (-1, 0)]]

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x,y in figures_pos] for figures_pos in figures_position]
figures_rect = pygame.Rect(0, 0, Tile - 2, Tile - 2)
field = [[0 for i in range(W)] for j in range(H)]

animation_count, animation_speed, animation_limit = 0, 60, 2000

background = pygame.image.load('galaxy2.jpg').convert()
game_background = pygame.image.load('galaxy1.jpg').convert()

main_font = pygame.font.Font('8BitLimitBrk.ttf', 80)
font = pygame.font.Font('8BitLimitBrk.ttf', 60)

title_tetris = main_font.render('TETRIS', True, pygame.Color('purple'))
title_score = font.render('Score', True, pygame.Color('pink'))
title_record = font.render('Record', True, pygame.Color('pink'))

get_color = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True

def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')

def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))


while True:
    record = get_record()
    dx, rotate = 0, False
    sc.blit(background, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_background, (0, 0))
    #delay for full lines
    for i in range(lines):
        pygame.time.wait(200)
    #control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                animation_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
    #move x
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break
    #move y
    animation_count += animation_speed
    if animation_count > animation_limit:
        animation_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                animation_limit = 2000
                break
    #rotate
    centre = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - centre.y
            y = figure[i].x - centre.x
            figure[i].x = centre.x - x
            figure[i].y = centre.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break
    #check line
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            animation_speed += 3
            lines += 1
    #score
    score += scores[lines]
    #draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]
    #draw figure
    for i in range(4):
        figures_rect.x = figure[i].x * Tile
        figures_rect.y = figure[i].y * Tile
        pygame.draw.rect(game_sc, color, figures_rect)
    #draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figures_rect.x, figures_rect.y = x * Tile, y * Tile
                pygame.draw.rect(game_sc, col, figures_rect)
    #draw next figure
    for i in range(4):
        figures_rect.x = next_figure[i].x * Tile + 390
        figures_rect.y = next_figure[i].y * Tile + 200
        pygame.draw.rect(sc, next_color, figures_rect)
    #draw titles
    sc.blit(title_tetris, (510, 15))
    sc.blit(title_score, (540, 780))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (600, 860))
    sc.blit(title_record, (530, 620))
    sc.blit(font.render(record, True, pygame.Color('white')), (600, 700))
    #game over
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)

    pygame.display.flip()
    clock.tick(FPS)
    pygame.display.set_caption('TETRIS by .arima')




