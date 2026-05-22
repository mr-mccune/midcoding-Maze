import sys

import pygame


pygame.init()

# Screen and timing constants
WIDTH = 800
HEIGHT = 600
TILE_SIZE = 40
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Escape")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FLOOR_COLOR = (30, 30, 30)
WALL_COLOR = (100, 100, 100)
PLAYER_COLOR = (50, 120, 255)
KEY_COLOR = (255, 220, 0)
EXIT_COLOR = (0, 200, 80)

font = pygame.font.SysFont(None, 32)

# W = wall, P = player start, K = key, E = exit, . = empty
level_map = [
	"WWWWWWWWWWWWWWWWWWWW",
	"WP.....W...........W",
	"W.WWW..W.WWWWW.WWW.W",
	"W...W..W.....W...W.W",
	"WWW.W..WWWWW.W.W.W.W",
	"W...W......W.W.W...W",
	"W.WWWWWW...W.W.WWW.W",
	"W......W.....W...W.W",
	"W.WWWW.WWWWWWW.W.W.W",
	"W.W..W.........W...W",
	"W.W..WWWWWWWWWWW.WWW",
	"W.W...............KW",
	"W.WWWWWWWWWWWWWWWW.W",
	"W.................EW",
	"WWWWWWWWWWWWWWWWWWWW",
]

player_size = TILE_SIZE - 8
player_speed = 4

walls = []
key_rect = None
exit_rect = None

player_x = 0
player_y = 0
start_x = 0
start_y = 0

has_key = False
game_state = "playing"
message = "Find the key, then reach the exit."


def load_level():
	"""Read the map and create wall/key/exit rectangles and player spawn."""
	global walls, key_rect, exit_rect
	global player_x, player_y, start_x, start_y

	walls = []
	key_rect = None
	exit_rect = None

	for row_index, row in enumerate(level_map):
		for col_index, tile in enumerate(row):
			x = col_index * TILE_SIZE
			y = row_index * TILE_SIZE

			if tile == "W":
				walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
			elif tile == "P":
				# Center the player within the tile since the player is slightly smaller.
				player_x = x + (TILE_SIZE - player_size) // 2
				player_y = y + (TILE_SIZE - player_size) // 2
				start_x = player_x
				start_y = player_y
			elif tile == "K":
				key_rect = pygame.Rect(x + 8, y + 8, TILE_SIZE - 16, TILE_SIZE - 16)
			elif tile == "E":
				exit_rect = pygame.Rect(x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8)


def reset_game():
	"""Reset key state and player position so the game can be replayed."""
	global player_x, player_y, has_key, game_state, message

	player_x = start_x
	player_y = start_y
	has_key = False
	game_state = "playing"
	message = "Find the key, then reach the exit."


def draw_maze():
	"""Draw floor first, then walls, exit, and key if it has not been collected."""
	screen.fill(BLACK)

	for row_index, row in enumerate(level_map):
		for col_index, _tile in enumerate(row):
			x = col_index * TILE_SIZE
			y = row_index * TILE_SIZE
			pygame.draw.rect(screen, FLOOR_COLOR, pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

	for wall in walls:
		pygame.draw.rect(screen, WALL_COLOR, wall)

	if exit_rect is not None:
		pygame.draw.rect(screen, EXIT_COLOR, exit_rect)

	if key_rect is not None and not has_key:
		pygame.draw.rect(screen, KEY_COLOR, key_rect)


def move_player(keys):
	"""Move in four directions and roll back movement if a wall collision occurs."""
	global player_x, player_y

	old_x, old_y = player_x, player_y

	if keys[pygame.K_LEFT] or keys[pygame.K_a]:
		player_x -= player_speed
	if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
		player_x += player_speed
	if keys[pygame.K_UP] or keys[pygame.K_w]:
		player_y -= player_speed
	if keys[pygame.K_DOWN] or keys[pygame.K_s]:
		player_y += player_speed

	player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
	for wall in walls:
		if player_rect.colliderect(wall):
			player_x, player_y = old_x, old_y
			break


def check_key_collision(player_rect):
	"""Collect the key once when the player touches it."""
	global has_key, message

	if key_rect is not None and not has_key and player_rect.colliderect(key_rect):
		has_key = True
		message = "Key collected! Reach the exit."


def check_exit_collision(player_rect):
	"""Allow winning only after the key has been collected."""
	global game_state, message

	if exit_rect is None or not player_rect.colliderect(exit_rect):
		return

	if has_key:
		game_state = "win"
		message = "You escaped!"
	else:
		message = "Find the key first."


def draw_player():
	"""Draw and return the player rectangle for collision checks."""
	player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
	pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
	return player_rect


def draw_hud():
	"""Show key status and current game message below the maze."""
	key_text = "Key: Collected" if has_key else "Key: Not Found"
	maze_pixel_height = len(level_map) * TILE_SIZE
	hud_y = min(maze_pixel_height + 8, HEIGHT - 28)

	key_surface = font.render(key_text, True, WHITE)
	msg_surface = font.render(message, True, WHITE)
	screen.blit(key_surface, (12, hud_y))
	screen.blit(msg_surface, (220, hud_y))


def draw_win_screen():
	"""Draw a simple win screen with restart instructions."""
	screen.fill(BLACK)
	title = font.render("You escaped!", True, EXIT_COLOR)
	prompt = font.render("Press R to restart or ESC to quit", True, WHITE)
	screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 30))
	screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 10))


load_level()

running = True
while running:
	clock.tick(FPS)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False

			if game_state == "win" and event.key == pygame.K_r:
				reset_game()

	if game_state == "playing":
		keys = pygame.key.get_pressed()
		move_player(keys)

		draw_maze()
		player_rect = draw_player()
		check_key_collision(player_rect)
		check_exit_collision(player_rect)
		draw_hud()

	elif game_state == "win":
		draw_win_screen()

	pygame.display.flip()

pygame.quit()
sys.exit()
