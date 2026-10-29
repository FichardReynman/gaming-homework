"""Playable gray-box Pygame prototype: RAM Tower Rescue."""
from pathlib import Path
import sys
import pygame

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.game_data import load_challenge
from src.ram_puzzle import RAMPuzzle

WIDTH, HEIGHT = 1000, 700
FPS = 60
BG = (13, 20, 39)
PANEL = (23, 34, 60)
TEXT = (235, 243, 255)
MUTED = (161, 180, 207)
CYAN = (65, 224, 239)
GREEN = (86, 220, 151)
ORANGE = (255, 183, 77)
RED = (255, 105, 120)
PURPLE = (154, 128, 255)

def wrap_text(font, text, max_width):
    words, lines, line = text.split(), [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if font.size(candidate)[0] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def draw_wrapped(surface, font, text, color, x, y, max_width, line_gap=5):
    for line in wrap_text(font, text, max_width):
        surface.blit(font.render(line, True, color), (x, y))
        y += font.get_linesize() + line_gap
    return y

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("RAM Tower Rescue | Computer Science Explorer")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("menlo,consolas,monospace", 17)
        self.small = pygame.font.SysFont("menlo,consolas,monospace", 14)
        self.title_font = pygame.font.SysFont("menlo,consolas,monospace", 29, bold=True)
        self.big_font = pygame.font.SysFont("menlo,consolas,monospace", 22, bold=True)
        self.challenge = load_challenge("RAM-001")
        self.state = "ROOM"
        self.puzzle = RAMPuzzle()
        self.message = "Explore the room. Walk to the glowing terminal and press E."
        self.hint_visible = False
        self.player = pygame.Rect(130, 340, 30, 42)
        self.speed = 250
        self.terminal = pygame.Rect(710, 230, 100, 112)
        self.background = self._load_image("assets/environments/ram_tower_room.png", (WIDTH, HEIGHT))
        self.character = self._load_image("assets/characters/main_character_poc.png", (44, 58))
        self.running = True

    def _load_image(self, relative, size):
        path = ROOT / relative
        if not path.exists():
            return None
        try:
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(image, size)
        except pygame.error:
            return None

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000, 0.04)
            self._events()
            if self.state == "ROOM":
                self._move(dt)
            self._draw()
        pygame.quit()

    def _events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in ("PUZZLE", "SUCCESS", "FAILURE"):
                        self.state = "ROOM"
                        self.message = "Back in RAM Tower District. Press E near the terminal to try again."
                    else:
                        self.running = False
                elif self.state == "ROOM" and event.key == pygame.K_e:
                    if self._near_terminal():
                        self._open_puzzle()
                    else:
                        self.message = "Get closer to the glowing terminal, then press E."
                elif self.state == "PUZZLE":
                    if event.key == pygame.K_h:
                        self.hint_visible = not self.hint_visible
                    elif event.key == pygame.K_RETURN:
                        result = self.puzzle.submit()
                        self.message = result.message
                        self.state = "SUCCESS" if result.status == "success" else "FAILURE"
                    elif event.key == pygame.K_r:
                        self._retry()
                elif self.state in ("SUCCESS", "FAILURE") and event.key == pygame.K_r:
                    self._retry()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "PUZZLE":
                    self._puzzle_click(event.pos)
                elif self.state in ("SUCCESS", "FAILURE"):
                    if pygame.Rect(390, 555, 220, 48).collidepoint(event.pos):
                        self._retry()

    def _open_puzzle(self):
        self.puzzle.reset()
        self.state = "PUZZLE"
        self.hint_visible = False
        self.message = "Select an occupied inactive block to release it, then select free blocks to allocate."

    def _retry(self):
        self.puzzle.reset()
        self.state = "PUZZLE"
        self.hint_visible = False
        self.message = "Try again: release inactive memory, then allocate 3 blocks to the School Project App."

    def _near_terminal(self):
        expanded = self.terminal.inflate(95, 95)
        return self.player.colliderect(expanded)

    def _move(self, dt):
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        if dx and dy:
            scale = 0.7071
        else:
            scale = 1
        self.player.x += round(dx * self.speed * dt * scale)
        self.player.y += round(dy * self.speed * dt * scale)
        self.player.clamp_ip(pygame.Rect(35, 105, WIDTH - 70, HEIGHT - 145))

    def _puzzle_click(self, pos):
        # Memory block cards.
        for i, block in enumerate(self.puzzle.blocks):
            rect = self._block_rect(i)
            if rect.collidepoint(pos):
                if block.allocated_to_target:
                    result = self.puzzle.release_block(i)
                elif block.owner is None:
                    result = self.puzzle.allocate_block(i)
                else:
                    result = self.puzzle.release_block(i)
                self.message = result.message
                if result.status == "failure":
                    self.state = "FAILURE"
                return
        if pygame.Rect(690, 570, 245, 48).collidepoint(pos):
            result = self.puzzle.submit()
            self.message = result.message
            self.state = "SUCCESS" if result.status == "success" else "FAILURE"
        elif pygame.Rect(420, 570, 245, 48).collidepoint(pos):
            self.hint_visible = not self.hint_visible
        elif pygame.Rect(150, 570, 245, 48).collidepoint(pos):
            self._retry()

    def _block_rect(self, i):
        x = 80 + (i % 3) * 295
        y = 335 + (i // 3) * 100
        return pygame.Rect(x, y, 260, 78)

    def _draw_room(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((8, 15, 32, 90))
            self.screen.blit(overlay, (0, 0))
        else:
            self.screen.fill(BG)
            # Subtle circuit-board floor grid.
            for x in range(30, WIDTH, 40):
                pygame.draw.line(self.screen, (24, 39, 67), (x, 90), (x, HEIGHT - 35), 1)
            for y in range(100, HEIGHT, 40):
                pygame.draw.line(self.screen, (24, 39, 67), (30, y), (WIDTH - 30, y), 1)
            pygame.draw.rect(self.screen, (19, 29, 51), (30, 90, WIDTH - 60, HEIGHT - 125), 3, border_radius=20)
            # Glowing memory modules in the room.
            for x, y, col in [(155, 155, PURPLE), (360, 165, CYAN), (490, 500, GREEN), (840, 475, PURPLE)]:
                pygame.draw.rect(self.screen, (25, 43, 72), (x, y, 55, 72), border_radius=9)
                pygame.draw.rect(self.screen, col, (x, y, 55, 72), 2, border_radius=9)
                pygame.draw.line(self.screen, col, (x + 12, y + 18), (x + 43, y + 18), 3)
                pygame.draw.line(self.screen, col, (x + 12, y + 31), (x + 43, y + 31), 3)
        pygame.draw.rect(self.screen, PANEL, (0, 0, WIDTH, 80))
        self.screen.blit(self.title_font.render("RAM TOWER DISTRICT", True, TEXT), (32, 19))
        self.screen.blit(self.small.render("ZONE 01  /  MEMORY MANAGEMENT", True, CYAN), (WIDTH - 365, 29))
        # Terminal body and glow.
        glow = self.terminal.inflate(28, 28)
        pygame.draw.rect(self.screen, (24, 73, 97), glow, border_radius=20)
        pygame.draw.rect(self.screen, (23, 44, 68), self.terminal, border_radius=14)
        pygame.draw.rect(self.screen, CYAN, self.terminal, 3, border_radius=14)
        pygame.draw.rect(self.screen, (9, 20, 37), (self.terminal.x + 13, self.terminal.y + 13, 74, 45), border_radius=6)
        pygame.draw.line(self.screen, GREEN, (self.terminal.x + 23, self.terminal.y + 28), (self.terminal.x + 74, self.terminal.y + 28), 3)
        pygame.draw.line(self.screen, CYAN, (self.terminal.x + 23, self.terminal.y + 40), (self.terminal.x + 58, self.terminal.y + 40), 3)
        pygame.draw.rect(self.screen, CYAN, (self.terminal.x + 25, self.terminal.y + 69, 50, 5), border_radius=3)
        self.screen.blit(self.small.render("RAM CONSOLE", True, TEXT), (self.terminal.x - 8, self.terminal.bottom + 9))
        if self.character:
            self.screen.blit(self.character, self.player)
        else:
            pygame.draw.ellipse(self.screen, (0, 0, 0), (self.player.x - 2, self.player.bottom - 7, self.player.width + 4, 12))
            pygame.draw.rect(self.screen, (247, 190, 112), (self.player.x + 6, self.player.y, 18, 18), border_radius=7)
            pygame.draw.rect(self.screen, PURPLE, (self.player.x + 3, self.player.y + 15, 24, 22), border_radius=7)
            pygame.draw.rect(self.screen, (49, 68, 102), (self.player.x + 4, self.player.y + 34, 8, 8), border_radius=3)
            pygame.draw.rect(self.screen, (49, 68, 102), (self.player.x + 18, self.player.y + 34, 8, 8), border_radius=3)
        if self._near_terminal():
            prompt = "PRESS E TO START RAM TOWER RESCUE"
            box = pygame.Rect(300, 605, 400, 42)
            pygame.draw.rect(self.screen, PANEL, box, border_radius=9)
            pygame.draw.rect(self.screen, CYAN, box, 1, border_radius=9)
            self.screen.blit(self.small.render(prompt, True, CYAN), (box.x + 18, box.y + 13))
        pygame.draw.rect(self.screen, (16, 25, 44), (0, HEIGHT - 34, WIDTH, 34))
        self.screen.blit(self.small.render("MOVE: WASD / ARROWS     INTERACT: E     QUIT: ESC", True, MUTED), (32, HEIGHT - 25))
        self._message_bar()

    def _message_bar(self):
        pygame.draw.rect(self.screen, (18, 29, 51), (24, 86, WIDTH - 48, 35), border_radius=7)
        draw_wrapped(self.screen, self.small, self.message, TEXT, 36, 95, WIDTH - 80, 0)

    def _draw_puzzle(self):
        self.screen.fill(BG)
        pygame.draw.rect(self.screen, (17, 29, 53), (0, 0, WIDTH, 90))
        self.screen.blit(self.title_font.render("RAM TOWER RESCUE", True, TEXT), (32, 20))
        self.screen.blit(self.small.render(f"{self.challenge['challenge_id']}  /  {self.challenge['cs_topic']}", True, CYAN), (34, 59))
        self.screen.blit(self.big_font.render("Memory Allocation Console", True, TEXT), (65, 112))
        draw_wrapped(self.screen, self.font, self.challenge["player_objective"], MUTED, 65, 148, 850)
        # Status counters
        pygame.draw.rect(self.screen, PANEL, (65, 205, 870, 94), border_radius=12)
        self.screen.blit(self.small.render("TARGET PROGRAM", True, MUTED), (85, 220))
        self.screen.blit(self.big_font.render("School Project App  •  ACTIVE", True, GREEN), (85, 245))
        self.screen.blit(self.small.render(f"Allocated: {self.puzzle.target_count}/3 blocks     Free: {self.puzzle.free_count}", True, TEXT), (575, 245))
        for i, block in enumerate(self.puzzle.blocks):
            rect = self._block_rect(i)
            if block.allocated_to_target:
                color, title, subtitle = GREEN, "SCHOOL PROJECT APP", "Allocated to target"
            elif block.owner is None:
                color, title, subtitle = CYAN, "AVAILABLE MEMORY", "Free block — click to allocate"
            elif block.protected:
                color, title, subtitle = RED, block.owner.upper(), "ACTIVE • PROTECTED"
            else:
                color, title, subtitle = ORANGE, block.owner.upper(), "INACTIVE • releasable"
            pygame.draw.rect(self.screen, (22, 37, 63), rect, border_radius=10)
            pygame.draw.rect(self.screen, color, rect, 2, border_radius=10)
            pygame.draw.circle(self.screen, color, (rect.x + 22, rect.y + 24), 6)
            self.screen.blit(self.small.render(f"BLOCK {i + 1}", True, MUTED), (rect.x + 38, rect.y + 11))
            self.screen.blit(self.font.render(title, True, TEXT), (rect.x + 14, rect.y + 32))
            self.screen.blit(self.small.render(subtitle, True, color), (rect.x + 14, rect.y + 55))
        draw_wrapped(self.screen, self.small, self.message, TEXT, 70, 545, 860, 0)
        if self.hint_visible:
            pygame.draw.rect(self.screen, (35, 44, 76), (65, 505, 870, 35), border_radius=7)
            draw_wrapped(self.screen, self.small, "HINT: " + self.challenge["hint_text"], ORANGE, 78, 514, 840, 0)
        self._button((150, 605, 245, 46), "RETRY (R)", PURPLE)
        self._button((420, 605, 245, 46), "HINT (H)", ORANGE)
        self._button((690, 605, 245, 46), "SUBMIT (ENTER)", GREEN)
        self.screen.blit(self.small.render("Click a block to release/allocate it  •  ESC returns to room", True, MUTED), (65, 665))

    def _button(self, rect, label, color):
        r = pygame.Rect(rect)
        pygame.draw.rect(self.screen, (24, 38, 65), r, border_radius=9)
        pygame.draw.rect(self.screen, color, r, 2, border_radius=9)
        rendered = self.font.render(label, True, color)
        self.screen.blit(rendered, rendered.get_rect(center=r.center))

    def _draw_result(self):
        self.screen.fill(BG)
        success = self.state == "SUCCESS"
        color = GREEN if success else RED
        heading = "RESCUE COMPLETE!" if success else "MEMORY ALLOCATION FAILED"
        self.screen.blit(self.title_font.render(heading, True, color), (70, 75))
        pygame.draw.rect(self.screen, PANEL, (70, 135, 860, 230), border_radius=16)
        draw_wrapped(self.screen, self.big_font, self.message, TEXT, 100, 165, 800, 7)
        if success:
            recap = ("RAM is finite: a computer has a limited amount of fast working memory. "
                     "Programs that are active need their data to remain available. You can reclaim "
                     "memory from inactive programs, but overwriting data still used by an active "
                     "program can break it.")
        else:
            recap = ("Remember: active programs may still need their memory. Release only blocks "
                     "owned by inactive programs, then assign at least 3 free blocks to the School "
                     "Project App. Retry and try a different sequence.")
        self.screen.blit(self.big_font.render("WHAT TO REMEMBER", True, CYAN), (100, 395))
        draw_wrapped(self.screen, self.font, recap, TEXT, 100, 435, 800, 6)
        self._button((390, 555, 220, 48), "RETRY (R)", GREEN if success else ORANGE)
        self.screen.blit(self.small.render("ESC: return to room", True, MUTED), (420, 625))

    def _draw(self):
        if self.state == "ROOM":
            self._draw_room()
        elif self.state == "PUZZLE":
            self._draw_puzzle()
        else:
            self._draw_result()
        pygame.display.flip()

if __name__ == "__main__":
    Game().run()
