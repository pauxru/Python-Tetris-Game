import pygame
from copy import deepcopy
from random import randrange, choice

width, height = 10, 20
tile = 45
game_win = width * tile, height * tile
win = 750, 940
FPS = 60

pygame.init()
game = pygame.display.set_mode(win)
game_main = pygame.Surface(game_win)
clock = pygame.time.Clock()

grid = [pygame.Rect(x * tile, y * tile, tile, tile) for x in range(width) for y in range(height)]

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

figures = [[pygame.Rect(x + width // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, tile - 2, tile - 2)
field = [[0 for i in range(width)] for j in range(height)]
fig_count, fig_speed, fig_limit = 0, 60, 2000


# random color for figures
get_color = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))

# next figure
figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

# background
bg = pygame.image.load("img/stars.jpg").convert()
game_bg = pygame.image.load("img/stars.jpg").convert()

# fonts / text
main_font = pygame.font.Font("font/LomoCopy.ttf", 55)
font = pygame.font.Font("font/commodore.ttf", 30)

title = main_font.render("TETRIS", True, pygame.Color("white"))
title_score = font.render("score:", True, pygame.Color("white"))
title_record = font.render("record:", True, pygame.Color("white"))
title_next = font.render("next:", True, pygame.Color("white"))


# scores
score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


def borders():
    if figure[i].x < 0 or figure[i].x > width - 1:
        return False
    elif figure[i].y > height - 1 or field[figure[i].y][figure[i].x]:
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
    game.blit(bg, (0, 0))
    game.blit(game_main, (20, 20))
    game_main.blit(game_bg, (0, 0))
    # delay for full lines
    for i in range(lines):
        pygame.time.wait(200)
    # control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                fig_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
    # move x
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not borders():
            figure = deepcopy(figure_old)
            break
    # move y
    fig_count += fig_speed
    if fig_count > fig_limit:
        fig_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                fig_limit = 2000
                break
    # rotate
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not borders():
                figure = deepcopy(figure_old)
                break
    # check lines
    line, lines = height - 1, 0
    for row in range(height - 1, -1, -1):
        count = 0
        for i in range(width):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < width:
            line -= 1
        else:
            fig_speed += 3
            lines += 1
    # compute score
    score += scores[lines]
    # draw grid
    [pygame.draw.rect(game_main, (40, 40, 40), i_rect, 1) for i_rect in grid]
    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * tile
        figure_rect.y = figure[i].y * tile
        pygame.draw.rect(game_main, color, figure_rect)
    # draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * tile, y * tile
                pygame.draw.rect(game_main, col, figure_rect)
   # draw text
    game.blit(title, (480, 16))
    game.blit(title_score, (500, 780))
    game.blit(font.render(str(score), True, pygame.Color("white")), (500, 832))
    game.blit(title_record, (500, 650))
    game.blit(font.render(record, True, pygame.Color("white")), (500, 702))
    game.blit(title_next, (500, 200))

    # draw boxes
    pygame.draw.rect(game, "white", (490, 649, 240, 100), 1)
    pygame.draw.rect(game, "white", (490, 779, 240, 100), 1)
    pygame.draw.rect(game, "white", (490, 199, 240, 300), 1)

    pygame.draw.rect(game, "white", (490, 649, 240, 40), 1)
    pygame.draw.rect(game, "white", (490, 779, 240, 40), 1)
    pygame.draw.rect(game, "white", (490, 199, 240, 40), 1)

    # draw next figure
    for i in range(4):
        figure_rect.x = next_figure[i].x * tile + 380
        figure_rect.y = next_figure[i].y * tile + 300
        pygame.draw.rect(game, next_color, figure_rect)


    # game over
    for i in range(width):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(width)] for i in range(height)]
            fig_count, fig_speed, fig_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_main, get_color(), i_rect)
                game.blit(game_main, (20, 20))
                pygame.display.flip()
                clock.tick(200)

    pygame.display.flip()
    clock.tick(FPS)