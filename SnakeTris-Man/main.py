import pygame
import random
import math

WIDTH = 1200
HEIGHT = 920
CELL = 20

FPS = 10

BLACK = (20, 20, 20)
GREEN = (0, 220, 0)
RED = (220, 50, 50)
BLUE = (50, 50, 255)
WHITE = (240, 240, 240)
YELLOW = (255, 220, 0)
PURPLE = (180, 0, 255)
CYAN = (0, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake + Pacman Ghost + Tetris Food")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 28)

TETRIS_SHAPES = [
    [[1, 1, 1, 1]],

    [[1, 1],
     [1, 1]],

    [[0, 1, 0],
     [1, 1, 1]],

    [[1, 0, 0],
     [1, 1, 1]],

    [[0, 0, 1],
     [1, 1, 1]],

    [[0, 1, 1],
     [1, 1, 0]],

    [[1, 1, 0],
     [0, 1, 1]]
]


snake = [(100, 100)]
direction = (CELL, 0)

def spawn_tetris():
    shape = random.choice(TETRIS_SHAPES)

    x = random.randint(5, (WIDTH // CELL) - 8) * CELL
    y = random.randint(5, (HEIGHT // CELL) - 8) * CELL

    blocks = []

    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col] == 1:
                blocks.append((x + col * CELL, y + row * CELL))

    return blocks


tetris_food = spawn_tetris()

# PACMAN DOT
def spawn_dot():
    return (
        random.randint(1, WIDTH // CELL - 2) * CELL,
        random.randint(1, HEIGHT // CELL - 2) * CELL
    )


power_dot = spawn_dot()
power_mode = False
power_timer = 0

# GHOST
ghost = [600, 400]
ghost_alive = True
ghost_respawn_timer = 0

score = 0

def draw_snake():
    for part in snake:
        pygame.draw.rect(screen, GREEN, (part[0], part[1], CELL, CELL))


def draw_tetris():
    for block in tetris_food:
        pygame.draw.rect(screen, PURPLE, (block[0], block[1], CELL, CELL))


def draw_dot():
    pygame.draw.circle(
        screen,
        CYAN,
        (power_dot[0] + CELL // 2, power_dot[1] + CELL // 2),
        CELL // 3
    )


def draw_ghost():
    if ghost_alive:
        color = BLUE if power_mode else RED

        pygame.draw.circle(
            screen,
            color,
            (ghost[0] + CELL // 2, ghost[1] + CELL // 2),
            CELL // 2
        )

        # eyes
        pygame.draw.circle(screen, WHITE,
                           (ghost[0] + 7, ghost[1] + 8), 3)
        pygame.draw.circle(screen, WHITE,
                           (ghost[0] + 13, ghost[1] + 8), 3)


def move_ghost():
    if not ghost_alive:
        return

    head_x, head_y = snake[0]

    dx = head_x - ghost[0]
    dy = head_y - ghost[1]

    dist = math.sqrt(dx * dx + dy * dy)

    if dist != 0:
        dx /= dist
        dy /= dist

    speed = 4

    if power_mode:
        speed = -3

    ghost[0] += int(dx * speed)
    ghost[1] += int(dy * speed)


def respawn_ghost():
    global ghost_alive

    ghost[0] = random.randint(1, WIDTH // CELL - 2) * CELL
    ghost[1] = random.randint(1, HEIGHT // CELL - 2) * CELL
    ghost_alive = True


def draw_score():
    txt = font.render(f"Score: {score}", True, WHITE)
    screen.blit(txt, (10, 10))


# GAME LOOP
running = True

while running:
    clock.tick(FPS)

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP and direction != (0, CELL):
                direction = (0, -CELL)

            elif event.key == pygame.K_DOWN and direction != (0, -CELL):
                direction = (0, CELL)

            elif event.key == pygame.K_LEFT and direction != (CELL, 0):
                direction = (-CELL, 0)

            elif event.key == pygame.K_RIGHT and direction != (-CELL, 0):
                direction = (CELL, 0)

    # MOVE SNAKE
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    snake.insert(0, new_head)

    ate = False

    # EAT TETRIS BLOCK
    for block in tetris_food[:]:
        if new_head == block:
            tetris_food.remove(block)
            score += 1
            ate = True

    if len(tetris_food) == 0:
        tetris_food = spawn_tetris()

    if not ate:
        snake.pop()

    # POWER DOT
    if new_head == power_dot:
        power_mode = True
        power_timer = pygame.time.get_ticks()
        power_dot = spawn_dot()

    if power_mode:
        if pygame.time.get_ticks() - power_timer > 7000:
            power_mode = False

    # GHOST
    move_ghost()

    # ghost collision
    if ghost_alive:
        snake_rect = pygame.Rect(new_head[0], new_head[1], CELL, CELL)
        ghost_rect = pygame.Rect(ghost[0], ghost[1], CELL, CELL)

        if snake_rect.colliderect(ghost_rect):

            if power_mode:
                ghost_alive = False
                ghost_respawn_timer = pygame.time.get_ticks()
                score += 10
            else:
                running = False

    # ghost respawn
    if not ghost_alive:
        if pygame.time.get_ticks() - ghost_respawn_timer > 5000:
            respawn_ghost()

    # WALL COLLISION
    if (
        new_head[0] < 0 or
        new_head[0] >= WIDTH or
        new_head[1] < 0 or
        new_head[1] >= HEIGHT
    ):
        running = False

    # SELF COLLISION
    if new_head in snake[1:]:
        running = False

    # DRAW
    screen.fill(BLACK)

    draw_snake()
    draw_tetris()
    draw_dot()
    draw_ghost()
    draw_score()

    if power_mode:
        txt = font.render("POWER MODE!", True, YELLOW)
        screen.blit(txt, (WIDTH - 230, 10))

    pygame.display.flip()

screen.fill(BLACK)

txt = font.render(f"GAME OVER! Score: {score}", True, RED)
screen.blit(txt, (WIDTH // 2 - 180, HEIGHT // 2))

pygame.display.flip()

pygame.time.delay(4000)

pygame.quit()