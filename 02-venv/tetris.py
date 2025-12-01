import pygame
import random

# --- 설정값 ---
cols = 10  # 가로 칸 수
rows = 20  # 세로 칸 수
cell_size = 30
colors = [
    (0, 0, 0), (255, 85, 85), (100, 200, 115), (120, 108, 245), 
    (255, 140, 50), (50, 120, 220), (180, 76, 130), (165, 161, 52)
]

# 테트리스 블록 모양 정의 (7가지)
tetris_shapes = [
    [[1, 1, 1, 1]], 
    [[2, 2], [2, 2]], 
    [[3, 0, 0], [3, 3, 3]], 
    [[0, 0, 4], [4, 4, 4]], 
    [[5, 5, 0], [0, 5, 5]], 
    [[0, 6, 6], [6, 6, 0]], 
    [[0, 7, 0], [7, 7, 7]]
]

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.new_figure()
        self.game_over = False

    def new_figure(self):
        self.shape = random.choice(tetris_shapes)
        self.color = tetris_shapes.index(self.shape) + 1
        self.x = 3
        self.y = 0

    def intersects(self, dx=0, dy=0, shape=None):
        shape = shape or self.shape
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x, new_y = self.x + j + dx, self.y + i + dy
                    if new_x < 0 or new_x >= cols or new_y >= rows or \
                       (new_y >= 0 and self.grid[new_y][new_x]):
                        return True
        return False

    def freeze(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.y + i][self.x + j] = self.color
        self.break_lines()
        self.new_figure()
        if self.intersects(): self.game_over = True

    def break_lines(self):
        # 0이 없는 행(꽉 찬 행)만 찾아서 제거하고 위에 빈 행 추가
        full_lines = [i for i, row in enumerate(self.grid) if 0 not in row]
        for i in full_lines:
            del self.grid[i]
            self.grid.insert(0, [0 for _ in range(cols)])

    def move(self, dx, dy):
        if not self.intersects(dx, dy):
            self.x += dx
            self.y += dy
            return True
        elif dy > 0: # 아래로 이동하다 충돌하면 고정
            self.freeze()
            return False

    def rotate(self):
        # 시계방향 회전 로직: 행렬의 전치 후 뒤집기
        new_shape = [list(row) for row in zip(*self.shape[::-1])]
        if not self.intersects(shape=new_shape):
            self.shape = new_shape

    def hard_drop(self):
        while not self.intersects(0, 1):
            self.y += 1
        self.freeze()

# --- 게임 실행 ---
pygame.init()
screen = pygame.display.set_mode((cols * cell_size, rows * cell_size))
clock = pygame.time.Clock()
game = Tetris()
fps, counter = 60, 0

running = True
while running:
    screen.fill((0, 0, 0))
    
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not game.game_over:
            if event.key == pygame.K_UP:    game.rotate()      # 시계방향 회전
            if event.key == pygame.K_LEFT:  game.move(-1, 0)   # 좌
            if event.key == pygame.K_RIGHT: game.move(1, 0)    # 우
            if event.key == pygame.K_DOWN:  game.move(0, 1)    # 빠르게 내리기
            if event.key == pygame.K_SPACE: game.hard_drop()   # 즉시 내리기

    # 자동 낙하 로직
    if not game.game_over:
        counter += 1
        if counter > fps // 2: # 속도 조절
            game.move(0, 1)
            counter = 0

    # 그리기: 이미 쌓인 블록
    for y, row in enumerate(game.grid):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(screen, colors[val], 
                                 (x * cell_size, y * cell_size, cell_size - 1, cell_size - 1))

    # 그리기: 현재 떨어지는 블록
    if not game.game_over:
        for i, row in enumerate(game.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, colors[game.color], 
                                     ((game.x + j) * cell_size, (game.y + i) * cell_size, cell_size - 1, cell_size - 1))
    else:
        # 게임 오버 시 붉은 테두리
        pygame.draw.rect(screen, (255, 0, 0), (0, 0, cols*cell_size, rows*cell_size), 5)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()