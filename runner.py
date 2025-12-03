import pygame
import sys
import time

from minesweeper import Minesweeper, MinesweeperAI

HEIGHT = 16
WIDTH = 16
MINES = 40

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
# AJOUT: Couleur jaune pour mise évidence
HIGHLIGHT = (255, 255, 100)

NUM_COLOR = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128),
             (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)]

# Create game
pygame.init()
size = width, height = 800, 600 
screen = pygame.display.set_mode(size)

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 40)
# AJOUT: Police pour statistiques
tinyFont = pygame.font.Font(OPEN_SANS, 16)

# Compute board size
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Add images
flag = pygame.image.load("assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))
mine = pygame.image.load("assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))

# Create game and AI agent
game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()
lost = False

# Show instructions initially
instructions = True

# AJOUT: Variables mode automatique 
ai_auto_mode = False
ai_speed = 500 
last_ai_move = pygame.time.get_ticks()

# AJOUT: Variables suivre et évidence dernier mouvement 
last_ai_cell = None
ai_move_highlight_time = 0

# AJOUT: Variables statistiques 
moves_count = 0
start_time = None

while True:

    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(BLACK)

    # Show game instructions
    if instructions:

        # Title
        title = largeFont.render("Play Minesweeper", True, WHITE)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 50)
        screen.blit(title, titleRect)

        # Rules
        rules = [
            "Click a cell to reveal it.",
            "Right-click a cell to mark it as a mine.",
            "Mark all mines successfully to win!",
        ]
        for i, rule in enumerate(rules):
            line = smallFont.render(rule, True, WHITE)
            lineRect = line.get_rect()
            lineRect.center = ((width / 2), 150 + 30 * i)
            screen.blit(line, lineRect)

        # Play game button
        buttonRect = pygame.Rect((width / 4), (3 / 4) * height, width / 2, 50)
        buttonText = mediumFont.render("Play Game", True, BLACK)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = buttonRect.center
        pygame.draw.rect(screen, WHITE, buttonRect)
        screen.blit(buttonText, buttonTextRect)

        # Check if play button clicked
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            mouse = pygame.mouse.get_pos()
            if buttonRect.collidepoint(mouse):
                instructions = False
                start_time = time.time()  # AJOUT: Démarrer chrono
                time.sleep(0.3)

        pygame.display.flip()
        continue

    # Draw board
    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):

            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            
            # AJOUT: Met en évidence nouvelle cellules révélé
            is_highlighted = (last_ai_cell == (i, j) and 
                            pygame.time.get_ticks() - ai_move_highlight_time < 1000 and
                            (i, j) in revealed)
            
            if (i, j) in revealed:
                # MODIFICATION: Utiliser couleur mise en évidence 
                color = HIGHLIGHT if is_highlighted else WHITE
                pygame.draw.rect(screen, color, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            # Add a mine, flag, or number if needed
            if game.is_mine((i, j)) and lost:
                screen.blit(mine, rect)
            elif (i, j) in flags:
                screen.blit(flag, rect)
            elif (i, j) in revealed:
                nearby = game.nearby_mines((i, j))
                if nearby:
                    neighbors = smallFont.render(
                        str(nearby),
                        True, NUM_COLOR[nearby - 1]
                    )
                    neighborsTextRect = neighbors.get_rect()
                    neighborsTextRect.center = rect.center
                    screen.blit(neighbors, neighborsTextRect)

            row.append(rect)
        cells.append(row)

    # MODIFICATION: Calculer dynamiquement position boutons
    button_x = (2 / 3) * width + BOARD_PADDING
    button_width = (width / 3) - BOARD_PADDING * 2
    button_height = 50
    button_spacing = 20

    # AI Move button
    aiButton = pygame.Rect(button_x, 50, button_width, button_height)
    buttonText = mediumFont.render("AI Move", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    pygame.draw.rect(screen, WHITE, aiButton)
    screen.blit(buttonText, buttonRect)

    # AJOUT: Bouton activer/désactiver mode automatique
    autoButton = pygame.Rect(button_x, 50 + button_height + button_spacing, 
                            button_width, button_height)
    auto_text = "AI Auto: ON" if ai_auto_mode else "AI Auto: OFF"
    auto_color = (0, 200, 0) if ai_auto_mode else WHITE
    buttonText = smallFont.render(auto_text, True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = autoButton.center
    pygame.draw.rect(screen, auto_color, autoButton)
    screen.blit(buttonText, buttonRect)

    # Reset button
    # MODIFICATION: Position ajustée pour nouveau bouton
    resetButton = pygame.Rect(button_x, 50 + 2 * (button_height + button_spacing), 
    button_width, button_height)
    buttonText = mediumFont.render("Reset", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    pygame.draw.rect(screen, WHITE, resetButton)
    screen.blit(buttonText, buttonRect)

    # AJOUT: Afficher statistiques IA 
    stats_y = 50 + 3 * (button_height + button_spacing) + 30
    ai_stats = ai.get_stats()
    
    stats_texts = [
        f"Moves: {moves_count}",
        f"Known mines: {ai_stats['known_mines']}",
        f"Known safes: {ai_stats['known_safes']}",
        f"Sentences: {ai_stats['sentences']}",
        f"Remaining: {ai_stats['cells_remaining']}"
    ]
    
    for i, stat_text in enumerate(stats_texts):
        stat = tinyFont.render(stat_text, True, WHITE)
        screen.blit(stat, (button_x + 10, stats_y + i * 25))

    # AJOUT: Afficher chrono
    if start_time and not lost and game.mines != flags:
        elapsed = int(time.time() - start_time)
        time_text = tinyFont.render(f"Time: {elapsed}s", True, WHITE)
        screen.blit(time_text, (button_x + 10, stats_y + len(stats_texts) * 25 + 20))

    # AJOUT: Afficher WON/LOST selon état position des stats
    status_y = stats_y + len(stats_texts) * 25 + 60
    
    if lost:
        status_text = "Lost!"
        status_color = (255, 50, 50)  # Rouge 
    elif game.mines == flags:
        status_text = "Won!"
        status_color = (50, 255, 50)  # Vert 
    else:
        status_text = ""
        status_color = WHITE
    
    if status_text:
        text = largeFont.render(status_text, True, status_color)
        textRect = text.get_rect()
        textRect.center = ((5 / 6) * width, status_y)
        screen.blit(text, textRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    # Check for a right-click to toggle flagging
    if right == 1 and not lost:
        mouse = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse) and (i, j) not in revealed:
                    if (i, j) in flags:
                        flags.remove((i, j))
                    else:
                        flags.add((i, j))
                    time.sleep(0.2)

    elif left == 1:
        mouse = pygame.mouse.get_pos()

        # If AI button clicked, make an AI move
        if aiButton.collidepoint(mouse) and not lost:
            move = ai.make_safe_move()
            if move is None:
                move = ai.make_random_move()
                if move is None:
                    flags = ai.mines.copy()
                    print("No moves left to make.")
                else:
                    print("No known safe moves, AI making random move.")
            else:
                print("AI making safe move.")
            
            # AJOUT: Enregistrer si nouvelle cellule
            if move and move not in revealed:
                last_ai_cell = move
                ai_move_highlight_time = pygame.time.get_ticks()
            
            time.sleep(0.2)

        # AJOUT: Gérer le clic bouton mode automatique
        elif autoButton.collidepoint(mouse):
            ai_auto_mode = not ai_auto_mode
            time.sleep(0.2)

        # Reset game state
        elif resetButton.collidepoint(mouse):
            game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
            revealed = set()
            flags = set()
            lost = False
            moves_count = 0  # AJOUT: Réinitialiser le compteur
            start_time = time.time()  # AJOUT: Réinitialiser chrono
            ai_auto_mode = False  # AJOUT: Désactiver mode automatique
            last_ai_cell = None  # AJOUT: Réinitialiser mise évidence
            continue

        # User-made move
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)

    # AJOUT: Logique mode automatique 
    if ai_auto_mode and not lost and game.mines != flags:
        current_time = pygame.time.get_ticks()
        if current_time - last_ai_move >= ai_speed:
            move = ai.make_safe_move()
            if move is None:
                move = ai.make_random_move()
                if move is None:
                    flags = ai.mines.copy()
                    ai_auto_mode = False  # Arrêter mode auto si aucun mouvement possible
                    print("No moves left to make.")
            
            # AJOUT: Enregistrer que si nouvelle cellule
            if move and move not in revealed:
                last_ai_cell = move
                ai_move_highlight_time = current_time
            
            last_ai_move = current_time

    # Make move and update AI knowledge
    def make_move(move):
        if game.is_mine(move):
            return True
        else:
            nearby = game.nearby_mines(move)
            revealed.add(move)
            ai.add_knowledge(move, nearby)
            if not nearby:
                # Loop over all cells within one row and column
                for i in range(move[0] - 1, move[0] + 2):
                    for j in range(move[1] - 1, move[1] + 2):

                        # Ignore the cell itself
                        if (i, j) == move:
                            continue

                        # Add to the cell collection if the cell is not yet explored
                        # and is not the mine already none
                        if 0 <= i < HEIGHT and 0 <= j < WIDTH and (i, j) not in revealed:
                            make_move((i, j))
        return False
    
    if move:
        moves_count += 1  # AJOUT: Incrémenter compteur mouvements
        if make_move(move):
            lost = True

    pygame.display.flip()