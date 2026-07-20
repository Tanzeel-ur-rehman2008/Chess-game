import sys
import pygame
import chess

# --- Configuration & Initialization ---
pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Premium Python Chess with Scoreboards")
clock = pygame.time.Clock()
FPS = 60

# Board Dimensions
DIMENSION = 8
BOARD_SIZE = min(WIDTH, HEIGHT) - 160
SQ_SIZE = BOARD_SIZE // DIMENSION
OFFSET_X = (WIDTH - BOARD_SIZE) // 2
OFFSET_Y = (HEIGHT - BOARD_SIZE) // 2

# Premium Color Palette
COLOR_TEXT = (240, 240, 240)
COLOR_TEXT_DIM = (140, 140, 140)
COLOR_PANEL_BG = (30, 35, 42, 220)
COLOR_PANEL_BORDER = (60, 65, 75)
COLOR_LIGHT = (235, 236, 208)
COLOR_DARK = (115, 149, 82)
COLOR_HIGHLIGHT = (246, 246, 105, 130)
COLOR_MOVE_DOT = (0, 0, 0, 50)
COLOR_BEZEL = (40, 42, 45)
COLOR_BEZEL_OUTLINE = (70, 72, 75)
COLOR_LEADER = (255, 215, 0)

# Game States
STATE_MENU = "MENU"
STATE_NEW_GAME = "NEW_GAME"
STATE_DIFFICULTY = "DIFFICULTY"
STATE_SETTINGS = "SETTINGS"
STATE_PLAYING = "PLAYING"

def get_font(size, bold=False):
    """Safely retrieves a system font with symbol fallbacks for chess glyph visibility."""
    for name in ['segoeuisymbol', 'segoe ui symbol', 'segoeui', 'arial', 'helvetica', 'sans-serif']:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            if font:
                return font
        except Exception:
            continue
    return pygame.font.Font(None, size)

# --- Pre-Render Background Gradient ---
def create_background_gradient():
    bg = pygame.Surface((1, HEIGHT))
    color_top, color_bottom = (25, 30, 40), (10, 12, 15)
    for y in range(HEIGHT):
        r = color_top[0] + (color_bottom[0] - color_top[0]) * y / HEIGHT
        g = color_top[1] + (color_bottom[1] - color_top[1]) * y / HEIGHT
        b = color_top[2] + (color_bottom[2] - color_top[2]) * y / HEIGHT
        pygame.draw.line(bg, (int(r), int(g), int(b)), (0, y), (1, y))
    return pygame.transform.scale(bg, (WIDTH, HEIGHT))

BACKGROUND = create_background_gradient()

# --- High-Quality Piece Generator ---
PIECE_IMAGES = {}
def pre_render_pieces():
    piece_symbols = {
        'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
        'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
    }
    large_size = SQ_SIZE * 3 
    font = get_font(int(large_size * 0.75), bold=True)
    
    for symbol, char in piece_symbols.items():
        is_white = symbol.isupper()
        text_color = (255, 255, 255) if is_white else (25, 25, 25)
        outline_color = (25, 25, 25) if is_white else (230, 230, 230)
        
        surface = pygame.Surface((large_size, large_size), pygame.SRCALPHA)
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
            img_outline = font.render(char, True, outline_color)
            surface.blit(img_outline, img_outline.get_rect(center=(large_size//2 + dx, large_size//2 + dy)))
            
        img = font.render(char, True, text_color)
        surface.blit(img, img.get_rect(center=(large_size//2, large_size//2)))
        PIECE_IMAGES[symbol] = pygame.transform.smoothscale(surface, (SQ_SIZE, SQ_SIZE))

pre_render_pieces()

GRAVEYARD_IMAGES = {}
def pre_render_graveyard_pieces():
    piece_symbols = {
        'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕',
        'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛'
    }
    size = 36
    font = get_font(int(size * 0.8), bold=True)
    
    for symbol, char in piece_symbols.items():
        is_white = symbol.isupper()
        text_color = (255, 255, 255) if is_white else (30, 30, 30)
        outline_color = (0, 0, 0) if is_white else (220, 220, 220)
        
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            img_outline = font.render(char, True, outline_color)
            surface.blit(img_outline, img_outline.get_rect(center=(size//2 + dx, size//2 + dy)))
            
        img = font.render(char, True, text_color)
        surface.blit(img, img.get_rect(center=(size//2, size//2)))
        GRAVEYARD_IMAGES[symbol] = surface

pre_render_graveyard_pieces()

# --- Advanced UI Components ---
class PremiumButton:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.is_pressed = False
        self.base_color = (55, 60, 65)
        self.hover_color = (75, 80, 85)
        self.shadow_color = (15, 15, 20)

    def draw(self, surface):
        offset = 4 if not self.is_pressed else 0
        shadow_rect = pygame.Rect(self.rect.x, self.rect.y + 4, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.shadow_color, shadow_rect, border_radius=12)
        
        btn_rect = pygame.Rect(self.rect.x, self.rect.y + (4 - offset), self.rect.width, self.rect.height)
        color = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(surface, color, btn_rect, border_radius=12)
        pygame.draw.rect(surface, (100, 105, 110), btn_rect, width=1, border_radius=12)
        
        font = get_font(28, bold=True)
        text_surf = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=btn_rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos, events):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_hovered: self.is_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_pressed and self.is_hovered:
                    self.is_pressed = False
                    return True
                self.is_pressed = False
        return False

def draw_menu_panel(surface, width, height):
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (30, 35, 40, 200), panel.get_rect(), border_radius=20)
    pygame.draw.rect(panel, (80, 85, 90, 150), panel.get_rect(), width=2, border_radius=20)
    surface.blit(panel, (WIDTH//2 - width//2, HEIGHT//2 - height//2 + 20))

def get_captured_pieces(board):
    starting_counts = {'P': 8, 'N': 2, 'B': 2, 'R': 2, 'Q': 1,
                       'p': 8, 'n': 2, 'b': 2, 'r': 2, 'q': 1}
    current_counts = {p: 0 for p in starting_counts}
    
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece and piece.symbol() in current_counts:
            current_counts[piece.symbol()] += 1
            
    captured_white, captured_black = [], []
    for symbol, start_count in starting_counts.items():
        missing = start_count - current_counts[symbol]
        if missing > 0:
            if symbol.isupper():
                captured_white.extend([symbol] * missing)
            else:
                captured_black.extend([symbol] * missing)
    return captured_white, captured_black

def calculate_material_scores(board):
    values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9}
    white_score, black_score = 0, 0
    
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece and piece.piece_type != chess.KING:
            val = values.get(piece.symbol().upper(), 0)
            if piece.color == chess.WHITE:
                white_score += val
            else:
                black_score += val
                
    return white_score - 39, black_score - 39

def draw_sidebars(surface, board):
    panel_width, panel_height = 280, BOARD_SIZE
    left_x = OFFSET_X - panel_width - 30
    right_x = OFFSET_X + BOARD_SIZE + 30
    
    left_rect = pygame.Rect(left_x, OFFSET_Y, panel_width, panel_height)
    right_rect = pygame.Rect(right_x, OFFSET_Y, panel_width, panel_height)
    
    for rect in [left_rect, right_rect]:
        sidebar_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(sidebar_surf, COLOR_PANEL_BG, sidebar_surf.get_rect(), border_radius=16)
        pygame.draw.rect(sidebar_surf, COLOR_PANEL_BORDER, sidebar_surf.get_rect(), width=2, border_radius=16)
        surface.blit(sidebar_surf, (rect.x, rect.y))
        
    font_name = get_font(22, bold=True)
    font_small = get_font(18)
    
    diff_white, diff_black = calculate_material_scores(board)
    
    # Determine Leader
    leader = "None"
    if diff_white > diff_black:
        leader = "White"
    elif diff_black > diff_white:
        leader = "Black"
        
    # Black Info
    black_turn = board.turn == chess.BLACK
    pygame.draw.rect(surface, (100, 150, 100) if black_turn else (50, 55, 65), (left_x + 15, OFFSET_Y + 15, panel_width - 30, 45), border_radius=8)
    surface.blit(font_name.render("Black Player", True, COLOR_TEXT), (left_x + 25, OFFSET_Y + 25))
    surface.blit(font_small.render(f"Advantage: +{diff_black}" if diff_black > 0 else "Advantage: 0", True, COLOR_TEXT_DIM), (left_x + 25, OFFSET_Y + 70))
    if leader == "Black":
        leader_surf = get_font(16, bold=True).render("👑 LEADING", True, COLOR_LEADER)
        surface.blit(leader_surf, (left_x + panel_width - 120, OFFSET_Y + 70))
    
    # White Info
    white_turn = board.turn == chess.WHITE
    pygame.draw.rect(surface, (100, 150, 100) if white_turn else (50, 55, 65), (right_x + 15, OFFSET_Y + 15, panel_width - 30, 45), border_radius=8)
    surface.blit(font_name.render("White Player", True, COLOR_TEXT), (right_x + 25, OFFSET_Y + 25))
    surface.blit(font_small.render(f"Advantage: +{diff_white}" if diff_white > 0 else "Advantage: 0", True, COLOR_TEXT_DIM), (right_x + 25, OFFSET_Y + 70))
    if leader == "White":
        leader_surf = get_font(16, bold=True).render("👑 LEADING", True, COLOR_LEADER)
        surface.blit(leader_surf, (right_x + panel_width - 120, OFFSET_Y + 70))
    
    cap_white, cap_black = get_captured_pieces(board)
    
    x_offset, y_offset = 20, 110
    for p in cap_white:
        if p in GRAVEYARD_IMAGES:
            surface.blit(GRAVEYARD_IMAGES[p], (left_x + x_offset, OFFSET_Y + y_offset))
            x_offset += 32
            if x_offset > panel_width - 50:
                x_offset, y_offset = 20, y_offset + 40
                
    x_offset, y_offset = 20, 110
    for p in cap_black:
        if p in GRAVEYARD_IMAGES:
            surface.blit(GRAVEYARD_IMAGES[p], (right_x + x_offset, OFFSET_Y + y_offset))
            x_offset += 32
            if x_offset > panel_width - 50:
                x_offset, y_offset = 20, y_offset + 40

def draw_board(surface):
    bezel_padding = 40
    bezel_rect = pygame.Rect(OFFSET_X - bezel_padding, OFFSET_Y - bezel_padding, 
                             BOARD_SIZE + bezel_padding*2, BOARD_SIZE + bezel_padding*2)
    pygame.draw.rect(surface, COLOR_BEZEL, bezel_rect, border_radius=8)
    pygame.draw.rect(surface, COLOR_BEZEL_OUTLINE, bezel_rect, width=3, border_radius=8)

    coord_font = get_font(16, bold=True)
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
            x = OFFSET_X + c * SQ_SIZE
            y = OFFSET_Y + r * SQ_SIZE
            pygame.draw.rect(surface, color, pygame.Rect(x, y, SQ_SIZE, SQ_SIZE))
            
            if r == 7:
                surface.blit(coord_font.render(chr(97 + c), True, COLOR_DARK if (r+c)%2==0 else COLOR_LIGHT), (x + SQ_SIZE - 15, y + SQ_SIZE - 25))
            if c == 0:
                surface.blit(coord_font.render(str(8 - r), True, COLOR_DARK if (r+c)%2==0 else COLOR_LIGHT), (x + 5, y + 5))

def draw_pieces(surface, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board.piece_at(chess.square(c, 7 - r))
            if piece:
                surface.blit(PIECE_IMAGES[piece.symbol()], (OFFSET_X + c * SQ_SIZE, OFFSET_Y + r * SQ_SIZE))

def highlight_squares(surface, board, selected_square):
    if selected_square is not None:
        s_col, s_row = chess.square_file(selected_square), 7 - chess.square_rank(selected_square)
        s_surf = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        s_surf.fill(COLOR_HIGHLIGHT)
        surface.blit(s_surf, (OFFSET_X + s_col * SQ_SIZE, OFFSET_Y + s_row * SQ_SIZE))
        
        for move in board.legal_moves:
            if move.from_square == selected_square:
                t_col, t_row = chess.square_file(move.to_square), 7 - chess.square_rank(move.to_square)
                dot_surf = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(dot_surf, COLOR_MOVE_DOT, (SQ_SIZE//2, SQ_SIZE//2), SQ_SIZE // 6)
                surface.blit(dot_surf, (OFFSET_X + t_col * SQ_SIZE, OFFSET_Y + t_row * SQ_SIZE))

def main():
    current_state = STATE_MENU
    board = chess.Board()
    selected_square = None
    
    btn_w, btn_h = 320, 65
    center_x = WIDTH // 2 - btn_w // 2
    start_y = HEIGHT // 2 - 80
    spacing = 85
    
    btn_new_game = PremiumButton(center_x, start_y, btn_w, btn_h, "New Game")
    btn_load_game = PremiumButton(center_x, start_y + spacing, btn_w, btn_h, "Saved Game")
    btn_settings = PremiumButton(center_x, start_y + spacing * 2, btn_w, btn_h, "Settings")
    btn_exit = PremiumButton(center_x, start_y + spacing * 3, btn_w, btn_h, "Exit Desktop")
    
    btn_single = PremiumButton(center_x, start_y, btn_w, btn_h, "Single Player")
    btn_multi = PremiumButton(center_x, start_y + spacing, btn_w, btn_h, "Multi Player")
    btn_back_menu = PremiumButton(center_x, start_y + spacing * 2, btn_w, btn_h, "Back to Menu")
    
    btn_easy = PremiumButton(center_x, start_y - spacing, btn_w, btn_h, "Easy")
    btn_med = PremiumButton(center_x, start_y, btn_w, btn_h, "Medium")
    btn_hard = PremiumButton(center_x, start_y + spacing, btn_w, btn_h, "Hard")
    btn_back_mode = PremiumButton(center_x, start_y + spacing * 2, btn_w, btn_h, "Back")
    
    btn_sound = PremiumButton(center_x, start_y, btn_w, btn_h, "Sound: ON")
    btn_google = PremiumButton(center_x, start_y + spacing, btn_w, btn_h, "Google Login")
    btn_set_back = PremiumButton(center_x, start_y + spacing * 2, btn_w, btn_h, "Back")
    sound_on = True

    running = True
    while running:
        screen.blit(BACKGROUND, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                
            if current_state == STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    col = (mouse_pos[0] - OFFSET_X) // SQ_SIZE
                    row = (mouse_pos[1] - OFFSET_Y) // SQ_SIZE
                    
                    if 0 <= col <= 7 and 0 <= row <= 7:
                        clicked_square = chess.square(col, 7 - row)
                        
                        if selected_square is not None:
                            move = chess.Move(selected_square, clicked_square)
                            piece = board.piece_at(selected_square)
                            
                            if piece and piece.piece_type == chess.PAWN:
                                if (row == 0 and board.turn == chess.WHITE) or (row == 7 and board.turn == chess.BLACK):
                                    move = chess.Move(selected_square, clicked_square, promotion=chess.QUEEN)

                            if move in board.legal_moves:
                                board.push(move)
                                selected_square = None
                            else:
                                clicked_piece = board.piece_at(clicked_square)
                                if clicked_piece and clicked_piece.color == board.turn:
                                    selected_square = clicked_square
                                else:
                                    selected_square = None
                        else:
                            piece = board.piece_at(clicked_square)
                            if piece and piece.color == board.turn:
                                selected_square = clicked_square
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = STATE_MENU

        if current_state != STATE_PLAYING:
            draw_menu_panel(screen, 420, 480)
            
        if current_state == STATE_MENU:
            # Startup Logo
            logo_font = get_font(60, bold=True)
            logo_surf = logo_font.render("♔", True, (255, 215, 0))
            screen.blit(logo_surf, logo_surf.get_rect(center=(WIDTH//2, start_y - 145)))

            title = get_font(70, bold=True).render("Python Chess", True, COLOR_TEXT)
            screen.blit(title, title.get_rect(center=(WIDTH//2, start_y - 85)))
            
            if btn_new_game.update(mouse_pos, events): current_state = STATE_NEW_GAME
            if btn_settings.update(mouse_pos, events): current_state = STATE_SETTINGS
            if btn_exit.update(mouse_pos, events): running = False
                
            for btn in [btn_new_game, btn_load_game, btn_settings, btn_exit]:
                btn.draw(screen)
                
        elif current_state == STATE_NEW_GAME:
            title = get_font(55, bold=True).render("Select Mode", True, COLOR_TEXT)
            screen.blit(title, title.get_rect(center=(WIDTH//2, start_y - 60)))
            
            if btn_single.update(mouse_pos, events): current_state = STATE_DIFFICULTY
            if btn_multi.update(mouse_pos, events):
                board.reset()
                current_state = STATE_PLAYING
            if btn_back_menu.update(mouse_pos, events): current_state = STATE_MENU
                
            for btn in [btn_single, btn_multi, btn_back_menu]:
                btn.draw(screen)
                
        elif current_state == STATE_DIFFICULTY:
            title = get_font(55, bold=True).render("AI Difficulty", True, COLOR_TEXT)
            screen.blit(title, title.get_rect(center=(WIDTH//2, start_y - 140)))
            
            if any(btn.update(mouse_pos, events) for btn in [btn_easy, btn_med, btn_hard]):
                board.reset()
                current_state = STATE_PLAYING
            if btn_back_mode.update(mouse_pos, events): current_state = STATE_NEW_GAME
                
            for btn in [btn_easy, btn_med, btn_hard, btn_back_mode]:
                btn.draw(screen)
                
        elif current_state == STATE_SETTINGS:
            title = get_font(55, bold=True).render("Settings", True, COLOR_TEXT)
            screen.blit(title, title.get_rect(center=(WIDTH//2, start_y - 60)))
            
            if btn_sound.update(mouse_pos, events):
                sound_on = not sound_on
                btn_sound.text = f"Sound: {'ON' if sound_on else 'OFF'}"
            if btn_google.update(mouse_pos, events): pass
            if btn_set_back.update(mouse_pos, events): current_state = STATE_MENU
                
            for btn in [btn_sound, btn_google, btn_set_back]:
                btn.draw(screen)
                
        elif current_state == STATE_PLAYING:
            draw_board(screen)
            highlight_squares(screen, board, selected_square)
            draw_pieces(screen, board)
            draw_sidebars(screen, board)
            
            instruction = get_font(20).render("Press ESC to return to Lobby", True, COLOR_TEXT_DIM)
            screen.blit(instruction, instruction.get_rect(center=(WIDTH//2, OFFSET_Y // 2)))
            
            if board.is_game_over():
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 190))
                screen.blit(overlay, (0, 0))
                text = get_font(85, bold=True).render(f"Game Over: {board.result()}", True, COLOR_TEXT)
                screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()