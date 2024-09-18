import pygame
import random
import time
from collections import Counter

# 初始化 Pygame
pygame.init()

# 初始化 Pygame mixer
pygame.mixer.init()

# 定义常量
WIDTH, HEIGHT = 720, 840
TILE_SIZE = 120
ROWS, COLS = 6, 6
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 102)  # 奶黄色
ORANGE = (102, 51, 0) #黄色

BG_COLOR = (200, 200, 200)
FONT_SIZE = 80
TIME_LIMIT_EASY = 40  # 倒计时时间（秒）- Easy模式
TIME_LIMIT_HARD = 30  # 倒计时时间（秒）- Hard模式

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("宇小波月饼铺")

# 加载主界面背景图片
main_background_image = pygame.image.load("background.png")
main_background_image = pygame.transform.scale(main_background_image, (WIDTH, HEIGHT))

# 加载游戏界面底图
bottom_image = pygame.image.load("bottom.png")
bottom_image = pygame.transform.scale(bottom_image, (WIDTH, HEIGHT))

# 加载图案图片
patterns = [pygame.image.load(f"pattern_{i}.png") for i in range(1, 7)]
patterns = [pygame.transform.scale(p, (TILE_SIZE, TILE_SIZE)) for p in patterns]

# 设置字体
font_path = "JosefinSans-Bold.ttf"
font_path2= "YeZiGongChangXiaoShiTou-2.ttf"

font = pygame.font.Font(font_path, FONT_SIZE)
welcome_font = pygame.font.Font(font_path2, 66)

# 创建奶黄色光标
cursor = pygame.Surface((TILE_SIZE, TILE_SIZE))
cursor.fill(YELLOW)
cursor.set_alpha(128)  # 设置光标透明度

# 加载按钮图片并缩放到100x100像素
pause_button_img = pygame.image.load("pause_button.png")
pause_button_img = pygame.transform.scale(pause_button_img, (100, 100))
exit_button_img = pygame.image.load("exit_button.png")
exit_button_img = pygame.transform.scale(exit_button_img, (100, 100))

# 定义按钮位置
pause_button_rect = pause_button_img.get_rect()
pause_button_rect.bottomright = (WIDTH - 10, HEIGHT - 10)
exit_button_rect = exit_button_img.get_rect()
exit_button_rect.bottomright = (WIDTH - 110, HEIGHT - 10)

# 加载游戏结算页面背景图片
game_over_background_image = pygame.image.load("final.png")
game_over_background_image = pygame.transform.scale(game_over_background_image, (WIDTH, HEIGHT))

# 加载背景音乐
bgm = pygame.mixer.Sound('bgm.mp3')
bgm.play(-1)  # 循环播放背景音乐

# 游戏状态标志
paused = False
paused_time = 0

# 初始化 selected 变量
selected = []

def draw_board(board):
    for row in range(ROWS):
        for col in range(COLS):
            tile = board[row][col]
            if tile is not None:
                screen.blit(tile, (col * TILE_SIZE, row * TILE_SIZE))
                if (row, col) in selected:
                    screen.blit(cursor, (col * TILE_SIZE, row * TILE_SIZE))

def check_match(difficulty, board):
    if len(selected) == 3:
        r1, c1 = selected[0]
        r2, c2 = selected[1]
        r3, c3 = selected[2]
        if board[r1][c1] == board[r2][c2] == board[r3][c3] and (r1, c1) != (r2, c2) and (r1, c1) != (r3, c3):
            board[r1][c1] = None
            board[r2][c2] = None
            board[r3][c3] = None
            return True
    selected.clear()
    return False

def draw_timer(time_left):
    timer_text = font.render(f"Time: {time_left}", True, BLACK)
    screen.blit(timer_text, (10, HEIGHT - FONT_SIZE - 10))

def is_game_over(board):
    for row in board:
        if any(tile is not None for tile in row):
            return False
    return True

def game_over_screen(result):
    screen.blit(game_over_background_image, (0, 0))  # 绘制结算页面背景
    result_text = "You Win! \(^o^)/" if result else "Game Over! ×_×"
    result_surface = font.render(result_text, True, BLACK)
    result_rect = result_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(result_surface, result_rect)
    pygame.display.flip()
    time.sleep(3)  # Display the result for 3 seconds

def main_menu():
    menu = True
    difficulty = None
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 345 < y < 445:  # Easy button
                    difficulty = 'easy'
                    menu = False
                elif 465 < y < 565:  # Hard button
                    difficulty = 'hard'
                    menu = False

        screen.blit(main_background_image, (0, 0))
        draw_text("宇小波月饼铺(*^_^*)", WIDTH / 2, 140, ORANGE, welcome_font)
        draw_text("Main Menu", WIDTH / 2, 240, BLACK, font)
        draw_text("Easy^o^", WIDTH / 2, 395, BLACK, font)
        draw_text("Hard>_<", WIDTH / 2, 515, BLACK, font)
        pygame.display.flip()

    return difficulty

def draw_text(text, x, y, color, font):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def generate_board(difficulty):
    total_tiles = ROWS * COLS
    pattern_counts = {pattern: (3 * (total_tiles // len(patterns) // 3)) for pattern in patterns}
    
    # 确保总数正确
    while sum(pattern_counts.values()) < total_tiles:
        for pattern in patterns:
            if sum(pattern_counts.values()) >= total_tiles:
                break
            pattern_counts[pattern] += 3

    board = []
    for _ in range(ROWS):
        row = []
        for _ in range(COLS):
            row.append(None)
        board.append(row)

    for pattern, count in pattern_counts.items():
        for _ in range(count):
            row = random.randint(0, ROWS - 1)
            col = random.randint(0, COLS - 1)
            while board[row][col] is not None:
                row = random.randint(0, ROWS - 1)
                col = random.randint(0, COLS - 1)
            board[row][col] = pattern

    return board

def game_loop(difficulty):
    global paused, paused_time
    running = True
    clock = pygame.time.Clock()
    game_success = False
    start_time = pygame.time.get_ticks()  # Reset start time

    # 设置倒计时时间
    time_limit = TIME_LIMIT_EASY if difficulty == 'easy' else TIME_LIMIT_HARD

    # 创建游戏板
    board = generate_board(difficulty)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if pause_button_rect.collidepoint((x, y)):
                    paused = not paused
                    if paused:
                        paused_time = pygame.time.get_ticks() - start_time
                    else:
                        start_time = pygame.time.get_ticks() - paused_time
                elif exit_button_rect.collidepoint((x, y)):
                    running = False
                elif not paused:
                    col, row = x // TILE_SIZE, y // TILE_SIZE
                    if board[row][col] is not None:
                        if not selected or (selected and (row, col) != selected[-1]):
                            selected.append((row, col))
                        if len(selected) == 3:
                            if check_match(difficulty, board):
                                selected.clear()  # Clear the selection after a match
                                if is_game_over(board):
                                    game_success = True
                                    running = False

        if not paused:
            clock.tick(FPS)
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
            time_left = max(0, time_limit - int(elapsed_time))

        screen.blit(bottom_image, (0, 0))  # Draw the bottom image first
        draw_board(board)
        draw_timer(time_left)
        screen.blit(pause_button_img, pause_button_rect)
        screen.blit(exit_button_img, exit_button_rect)
        pygame.display.flip()

        if time_left == 0 or is_game_over(board):
            game_success = is_game_over(board)
            running = False  # End the game loop

    game_over_screen(game_success)

    pygame.quit()

# 主程序
difficulty = main_menu()
game_loop(difficulty)




