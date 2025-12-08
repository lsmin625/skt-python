import pygame
import random

# ----- 기본 설정 -----
WIDTH, HEIGHT = 300, 600      # 게임 창 크기
COLS, ROWS = 10, 20           # 테트리스 보드 크기
CELL = WIDTH // COLS          # 한 칸의 픽셀 크기

FPS = 60
FALL_EVENT = pygame.USEREVENT + 1
FALL_SPEED = 500  # ms마다 한 칸씩 떨어지기

# ----- 블록 모양 정의 -----
# 각 모양은 회전을 쉽게 하기 위해 2D 배열로 정의
SHAPES = [
    # I
    [[1, 1, 1, 1]],
    # O
    [[1, 1],
     [1, 1]],
    # T
    [[0, 1, 0],
     [1, 1, 1]],
    # S
    [[0, 1, 1],
     [1, 1, 0]],
    # Z
    [[1, 1, 0],
     [0, 1, 1]],
    # J
    [[1, 0, 0],
     [1, 1, 1]],
    # L
    [[0, 0, 1],
     [1, 1, 1]],
]

COLORS = [
    (0, 255, 255),  # I - cyan
    (255, 255, 0),  # O - yellow
    (128, 0, 128),  # T - purple
    (0, 255, 0),    # S - green
    (255, 0, 0),    # Z - red
    (0, 0, 255),    # J - blue
    (255, 165, 0),  # L - orange
]


def rotate_shape(shape):
    """시계 방향 회전"""
    # zip(*shape[::-1])로 2D 배열을 회전한 뒤 다시 리스트로 변환
    return [list(row) for row in zip(*shape[::-1])]


class Piece:
    def __init__(self, x, y, shape_idx):
        self.x = x      # 보드 기준 x (컬럼)
        self.y = y      # 보드 기준 y (로우)
        self.shape_idx = shape_idx
        self.shape = SHAPES[shape_idx]
        self.color = COLORS[shape_idx]

    def get_cells(self):
        """현재 블록이 차지하는 보드 좌표 리스트 반환"""
        cells = []
        for dy, row in enumerate(self.shape):
            for dx, val in enumerate(row):
                if val:
                    cells.append((self.x + dx, self.y + dy))
        return cells


def create_grid(locked_positions):
    """보드(ROWS x COLS)에 이미 쌓인 블록을 반영해서 2D 배열 생성"""
    grid = [[(0, 0, 0) for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS:
            grid[y][x] = color
    return grid


def valid_space(piece, locked_positions):
    """블록이 보드 안에 있고, 다른 블록과 겹치지 않는지 검사"""
    accepted_positions = [
        (x, y) for x in range(COLS) for y in range(ROWS)
    ]
    for x, y in piece.get_cells():
        if (x, y) not in accepted_positions:
            return False
        if (x, y) in locked_positions:
            return False
    return True


def check_game_over(locked_positions):
    """보드 위쪽(ROW 0)에 블록이 있으면 게임 오버"""
    for (x, y) in locked_positions:
        if y < 1:
            return True
    return False


def clear_rows(locked_positions):
    """가득 찬 줄 제거하고, 위 줄들을 아래로 내림. (지운 줄 수, 갱신된 locked_positions) 반환"""
    rows_to_clear = []
    for y in range(ROWS):
        row_filled = True
        for x in range(COLS):
            if (x, y) not in locked_positions:
                row_filled = False
                break
        if row_filled:
            rows_to_clear.append(y)

    if not rows_to_clear:
        return 0, locked_positions

    # 해당 줄 제거
    for y in rows_to_clear:
        for x in range(COLS):
            locked_positions.pop((x, y), None)

    # 위에 있던 블록들 내려주기
    rows_to_clear.sort()
    for y in rows_to_clear:
        new_locked = {}
        for (x, yy), color in locked_positions.items():
            if yy < y:
                new_locked[(x, yy + 1)] = color
            else:
                new_locked[(x, yy)] = color
        locked_positions = new_locked

    return len(rows_to_clear), locked_positions


def get_new_piece():
    idx = random.randint(0, len(SHAPES) - 1)
    # 중앙에서 시작하도록 x 설정
    start_x = COLS // 2 - len(SHAPES[idx][0]) // 2
    return Piece(start_x, 0, idx)


def draw_grid_lines(surface):
    for x in range(COLS):
        pygame.draw.line(surface, (50, 50, 50), (x * CELL, 0), (x * CELL, HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface, (50, 50, 50), (0, y * CELL), (WIDTH, y * CELL))


def draw_window(surface, grid, score):
    surface.fill((0, 0, 0))
    # 이미 쌓인 블록 그리기
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color != (0, 0, 0):
                pygame.draw.rect(surface, color,
                                 (x * CELL, y * CELL, CELL, CELL))
    # 격자선
    draw_grid_lines(surface)

    # 점수 표시
    font = pygame.font.SysFont("malgungothic", 24)
    text = font.render(f"점수: {score}", True, (255, 255, 255))
    surface.blit(text, (10, 10))

    pygame.display.update()


def draw_piece(surface, piece):
    for x, y in piece.get_cells():
        if y >= 0:
            pygame.draw.rect(surface, piece.color,
                             (x * CELL, y * CELL, CELL, CELL))


def hard_drop(piece, locked_positions):
    """스페이스바: 한 번에 바닥까지 떨어뜨리기"""
    while True:
        test_piece = Piece(piece.x, piece.y + 1, piece.shape_idx)
        test_piece.shape = piece.shape
        if valid_space(test_piece, locked_positions):
            piece.y += 1
        else:
            break


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame Tetris (간단 버전)")
    clock = pygame.time.Clock()

    locked_positions = {}  # {(x, y): color}
    current_piece = get_new_piece()
    next_piece = get_new_piece()
    pygame.time.set_timer(FALL_EVENT, FALL_SPEED)
    fall_fast = False

    score = 0
    running = True

    while running:
        clock.tick(FPS)
        grid = create_grid(locked_positions)

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # 자동 떨어짐
            if event.type == FALL_EVENT:
                dy = 1
                if fall_fast:
                    dy = 2  # 아래키 누르고 있으면 더 빨리

                test_piece = Piece(current_piece.x, current_piece.y + dy, current_piece.shape_idx)
                test_piece.shape = current_piece.shape
                if valid_space(test_piece, locked_positions):
                    current_piece.y += dy
                else:
                    # 바닥에 닿으면 잠금
                    for pos in current_piece.get_cells():
                        locked_positions[pos] = current_piece.color

                    # 한 줄이 가득 찼는지 확인
                    cleared, locked_positions = clear_rows(locked_positions)
                    score += cleared * 100

                    # 새 블록 생성
                    current_piece = next_piece
                    next_piece = get_new_piece()

                    # 게임 오버 체크
                    if check_game_over(locked_positions):
                        running = False

            # 키 입력
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    test_piece = Piece(current_piece.x - 1, current_piece.y, current_piece.shape_idx)
                    test_piece.shape = current_piece.shape
                    if valid_space(test_piece, locked_positions):
                        current_piece.x -= 1

                elif event.key == pygame.K_RIGHT:
                    test_piece = Piece(current_piece.x + 1, current_piece.y, current_piece.shape_idx)
                    test_piece.shape = current_piece.shape
                    if valid_space(test_piece, locked_positions):
                        current_piece.x += 1

                elif event.key == pygame.K_DOWN:
                    # 아래 방향키: 빠르게 내리기 활성화
                    fall_fast = True

                elif event.key == pygame.K_UP:
                    # 위 방향키: 회전 (시계방향)
                    rotated_shape = rotate_shape(current_piece.shape)
                    test_piece = Piece(current_piece.x, current_piece.y, current_piece.shape_idx)
                    test_piece.shape = rotated_shape
                    if valid_space(test_piece, locked_positions):
                        current_piece.shape = rotated_shape

                elif event.key == pygame.K_SPACE:
                    # 스페이스: 하드 드롭
                    hard_drop(current_piece, locked_positions)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    fall_fast = False

        # 화면 그리기
        draw_window(screen, grid, score)
        draw_piece(screen, current_piece)
        pygame.display.update()

    # 게임 오버 화면
    font = pygame.font.SysFont("malgungothic", 36)
    screen.fill((0, 0, 0))
    text = font.render("게임 오버! ESC 키로 종료", True, (255, 255, 255))
    screen.blit(text, (20, HEIGHT // 2 - 20))
    pygame.display.update()

    # ESC 누르면 종료
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False

    pygame.quit()


if __name__ == "__main__":
    main()
