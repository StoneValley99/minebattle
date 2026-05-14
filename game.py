import pygame
import math
import random

pygame.init()

SCREEN_W, SCREEN_H = 1024, 768
GRID_SIZE = 48
COLS = SCREEN_W // GRID_SIZE   # 21
ROWS = (SCREEN_H - 120) // GRID_SIZE  # 13

# --- Gruvfärger ---
ROCK_BG       = (28, 24, 22)
ROCK_WALL     = (45, 38, 32)
ROCK_LINE     = (38, 32, 28)
ORE_COLOR     = (140, 60, 30)        # Järnmalm (magnetit, rödaktig)
ORE_VEIN      = (180, 90, 40)
TUNNEL_FLOOR  = (75, 65, 55)
TUNNEL_EDGE   = (55, 48, 40)
UI_BG         = (18, 15, 12)
UI_LINE       = (80, 65, 50)
WHITE         = (255, 255, 255)
BLACK         = (0, 0, 0)
RED           = (220, 50, 50)
YELLOW        = (255, 210, 30)       # LKAB-gul
LKAB_BLUE     = (0, 60, 140)
ORANGE        = (255, 130, 0)
WARN_YELLOW   = (255, 200, 0)
WARN_BLACK    = (30, 30, 30)
GRAY          = (110, 100, 90)
DARK_GRAY     = (55, 50, 45)
STEEL         = (140, 150, 160)
LIGHT_YELLOW  = (255, 230, 100)
GREEN         = (60, 200, 60)
DARK_GREEN    = (20, 120, 20)

# Banans vägpunkter (kolumn, rad)
WAYPOINTS = [
    (0, 2), (4, 2), (4, 6), (8, 6), (8, 2), (12, 2),
    (12, 10), (16, 10), (16, 6), (20, 6), (20, 12)
]

TOWER_TYPES = {
    "borrhammare": {
        "name": "Borrhammare", "cost": 75,
        "color": (200, 170, 50), "range": 110,
        "damage": 12, "fire_rate": 20,
        "bullet_color": (220, 200, 80), "bullet_speed": 7,
        "splash": 0, "slow": 0,
        "desc": "Snabb borrning, kort räckvidd",
    },
    "skrotare": {
        "name": "Skrotare", "cost": 125,
        "color": (80, 130, 200), "range": 130,
        "damage": 20, "fire_rate": 40,
        "bullet_color": (120, 180, 255), "bullet_speed": 5,
        "splash": 0, "slow": 70,
        "desc": "Saktar ner, medellång räckvidd",
    },
    "lhd": {
        "name": "LHD", "cost": 200,
        "color": ORANGE, "range": 105,
        "damage": 45, "fire_rate": 65,
        "bullet_color": (255, 160, 40), "bullet_speed": 5,
        "splash": 45, "slow": 0,
        "desc": "Skopsprängning, träffar flera",
    },
    "sprang": {
        "name": "Sprängare", "cost": 175,
        "color": (210, 40, 40), "range": 140,
        "damage": 80, "fire_rate": 110,
        "bullet_color": (255, 80, 40), "bullet_speed": 4,
        "splash": 60, "slow": 0,
        "desc": "Stor explosion, långsam laddning",
    },
}

ZOMBIE_WAVES = [
    [{"type": "normal", "count": 8,  "interval": 60}],
    [{"type": "normal", "count": 12, "interval": 50}, {"type": "fast", "count": 4, "interval": 40}],
    [{"type": "normal", "count": 10, "interval": 45}, {"type": "fast", "count": 6, "interval": 35}, {"type": "tank", "count": 2, "interval": 80}],
    [{"type": "fast",   "count": 15, "interval": 30}, {"type": "tank", "count": 4, "interval": 70}],
    [{"type": "normal", "count": 20, "interval": 40}, {"type": "fast", "count": 10, "interval": 30}, {"type": "tank", "count": 6, "interval": 60}, {"type": "boss", "count": 1, "interval": 1}],
]

ZOMBIE_STATS = {
    "normal": {"hp": 80,   "speed": 1.2, "reward": 10,  "color": (80, 170, 80),   "size": 10},
    "fast":   {"hp": 50,   "speed": 2.2, "reward": 15,  "color": (200, 200, 50),  "size": 8},
    "tank":   {"hp": 300,  "speed": 0.7, "reward": 30,  "color": (180, 80,  80),  "size": 14},
    "boss":   {"hp": 1000, "speed": 0.5, "reward": 100, "color": (200, 50,  200), "size": 20},
}


def grid_to_px(col, row):
    return col * GRID_SIZE + GRID_SIZE // 2, row * GRID_SIZE + GRID_SIZE // 2


def px_to_grid(x, y):
    return x // GRID_SIZE, y // GRID_SIZE


def build_path_cells():
    cells = set()
    for i in range(len(WAYPOINTS) - 1):
        c1, r1 = WAYPOINTS[i]
        c2, r2 = WAYPOINTS[i + 1]
        dc = (1 if c2 > c1 else -1) if c2 != c1 else 0
        dr = (1 if r2 > r1 else -1) if r2 != r1 else 0
        c, r = c1, r1
        while (c, r) != (c2, r2):
            cells.add((c, r))
            c += dc
            r += dr
        cells.add((c2, r2))
    return cells


PATH_CELLS = build_path_cells()


def make_mine_background(rng):
    """Pre-render a rocky mine background surface."""
    surf = pygame.Surface((SCREEN_W, ROWS * GRID_SIZE))
    surf.fill(ROCK_BG)

    # Rock wall base per cell
    for c in range(COLS):
        for r in range(ROWS):
            x, y = c * GRID_SIZE, r * GRID_SIZE
            if (c, r) not in PATH_CELLS:
                shade = rng.randint(-10, 10)
                col = tuple(max(0, min(255, v + shade)) for v in ROCK_WALL)
                pygame.draw.rect(surf, col, (x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2))

    # Ore veins
    for _ in range(28):
        cx = rng.randint(0, SCREEN_W)
        cy = rng.randint(0, ROWS * GRID_SIZE)
        gc, gr = px_to_grid(cx, cy)
        if (gc, gr) in PATH_CELLS:
            continue
        length = rng.randint(20, 80)
        angle = rng.uniform(0, math.pi * 2)
        thickness = rng.randint(1, 3)
        ex = int(cx + math.cos(angle) * length)
        ey = int(cy + math.sin(angle) * length)
        pygame.draw.line(surf, ORE_VEIN, (cx, cy), (ex, ey), thickness)
        # Small ore blobs
        for _ in range(rng.randint(2, 5)):
            bx = cx + rng.randint(-12, 12)
            by = cy + rng.randint(-12, 12)
            pygame.draw.circle(surf, ORE_COLOR, (bx, by), rng.randint(2, 5))

    # Random cracks in the rock
    for _ in range(60):
        sx = rng.randint(0, SCREEN_W)
        sy = rng.randint(0, ROWS * GRID_SIZE)
        gc, gr = px_to_grid(sx, sy)
        if (gc, gr) in PATH_CELLS:
            continue
        pts = [(sx, sy)]
        for _ in range(rng.randint(2, 5)):
            lx, ly = pts[-1]
            pts.append((lx + rng.randint(-14, 14), ly + rng.randint(-14, 14)))
        for i in range(len(pts) - 1):
            pygame.draw.line(surf, ROCK_LINE, pts[i], pts[i + 1], 1)

    # Tunnel floor
    for c, r in PATH_CELLS:
        x, y = c * GRID_SIZE, r * GRID_SIZE
        pygame.draw.rect(surf, TUNNEL_FLOOR, (x, y, GRID_SIZE, GRID_SIZE))
        # Worn edges
        pygame.draw.rect(surf, TUNNEL_EDGE, (x, y, GRID_SIZE, GRID_SIZE), 1)
        # Floor gravel dots
        for _ in range(4):
            gx = x + rng.randint(4, GRID_SIZE - 4)
            gy = y + rng.randint(4, GRID_SIZE - 4)
            pygame.draw.circle(surf, TUNNEL_EDGE, (gx, gy), 1)

    # Grid lines (subtle rock cracks)
    for c in range(COLS + 1):
        pygame.draw.line(surf, ROCK_LINE, (c * GRID_SIZE, 0), (c * GRID_SIZE, ROWS * GRID_SIZE), 1)
    for r in range(ROWS + 1):
        pygame.draw.line(surf, ROCK_LINE, (0, r * GRID_SIZE), (SCREEN_W, r * GRID_SIZE), 1)

    # Warning stripes at tunnel entrance/exit
    for wp in [WAYPOINTS[0], WAYPOINTS[-1]]:
        wx, wy = wp[0] * GRID_SIZE, wp[1] * GRID_SIZE
        for i in range(4):
            stripe_col = WARN_YELLOW if i % 2 == 0 else WARN_BLACK
            pygame.draw.rect(surf, stripe_col, (wx + i * (GRID_SIZE // 4), wy, GRID_SIZE // 4, GRID_SIZE))

    return surf


class Zombie:
    def __init__(self, ztype):
        stats = ZOMBIE_STATS[ztype]
        self.ztype = ztype
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.base_speed = stats["speed"]
        self.speed = self.base_speed
        self.reward = stats["reward"]
        self.color = stats["color"]
        self.size = stats["size"]
        self.waypoint_idx = 0
        px, py = grid_to_px(*WAYPOINTS[0])
        self.x = float(px)
        self.y = float(py)
        self.alive = True
        self.reached_end = False
        self.slow_timer = 0
        self.progress = 0.0

    def update(self):
        if self.slow_timer > 0:
            self.slow_timer -= 1
            self.speed = self.base_speed * 0.35
        else:
            self.speed = self.base_speed

        if self.waypoint_idx + 1 >= len(WAYPOINTS):
            self.reached_end = True
            self.alive = False
            return

        tx, ty = grid_to_px(*WAYPOINTS[self.waypoint_idx + 1])
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.x, self.y = float(tx), float(ty)
            self.waypoint_idx += 1
            self.progress += dist
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed
            self.progress += self.speed

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (0, 0, 0), (cx + 2, cy + 2), self.size)
        pygame.draw.circle(surface, self.color, (cx, cy), self.size)
        # Hjälm (gruvarbetare-look)
        helmet_col = (220, 180, 30) if self.ztype != "boss" else (200, 30, 200)
        pygame.draw.arc(surface, helmet_col,
                        (cx - self.size, cy - self.size - 2, self.size * 2, self.size + 2),
                        0, math.pi, 3)
        # Lampsko på hjälm
        pygame.draw.circle(surface, YELLOW, (cx, cy - self.size + 1), 2)
        # Ögon
        eye_off = max(2, self.size // 3)
        pygame.draw.circle(surface, WHITE, (cx - eye_off, cy - 2), 3)
        pygame.draw.circle(surface, WHITE, (cx + eye_off, cy - 2), 3)
        pygame.draw.circle(surface, BLACK, (cx - eye_off + 1, cy - 2), 1)
        pygame.draw.circle(surface, BLACK, (cx + eye_off + 1, cy - 2), 1)
        # HP-bar
        bar_w = self.size * 2
        bar_x = cx - self.size
        bar_y = cy - self.size - 10
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_w, 4))
        hp_w = int(bar_w * self.hp / self.max_hp)
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, hp_w, 4))
        # Fryst-ring
        if self.slow_timer > 0:
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), self.size + 3, 2)


class Bullet:
    def __init__(self, x, y, target, speed, damage, color, splash, slow):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.speed = speed
        self.damage = damage
        self.color = color
        self.splash = splash
        self.slow = slow
        self.alive = True

    def update(self, zombies):
        if not self.target.alive:
            best, best_dist = None, 9999
            for z in zombies:
                d = math.hypot(z.x - self.x, z.y - self.y)
                if d < best_dist:
                    best_dist, best = d, z
            if best and best_dist < 200:
                self.target = best
            else:
                self.alive = False
                return

        dx, dy = self.target.x - self.x, self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed + 4:
            self._hit(zombies)
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def _hit(self, zombies):
        self.alive = False
        if self.splash > 0:
            for z in zombies:
                if math.hypot(z.x - self.x, z.y - self.y) <= self.splash:
                    z.hp -= self.damage
                    if z.hp <= 0:
                        z.alive = False
                    if self.slow:
                        z.slow_timer = self.slow
        else:
            self.target.hp -= self.damage
            if self.target.hp <= 0:
                self.target.alive = False
            if self.slow:
                self.target.slow_timer = self.slow

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 4)
        # Glöd
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)


class Tower:
    def __init__(self, col, row, ttype):
        self.col = col
        self.row = row
        self.ttype = ttype
        data = TOWER_TYPES[ttype]
        self.color = data["color"]
        self.range = data["range"]
        self.damage = data["damage"]
        self.fire_rate = data["fire_rate"]
        self.bullet_color = data["bullet_color"]
        self.bullet_speed = data["bullet_speed"]
        self.splash = data["splash"]
        self.slow = data["slow"]
        self.cooldown = 0
        self.x, self.y = grid_to_px(col, row)
        self.angle = 0.0  # riktning mot senaste målet

    def update(self, zombies, bullets):
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        target = self._find_target(zombies)
        if target:
            self.angle = math.atan2(target.y - self.y, target.x - self.x)
            bullets.append(Bullet(
                self.x, self.y, target,
                self.bullet_speed, self.damage,
                self.bullet_color, self.splash, self.slow
            ))
            self.cooldown = self.fire_rate

    def _find_target(self, zombies):
        best, best_prog = None, -1
        for z in zombies:
            d = math.hypot(z.x - self.x, z.y - self.y)
            if d <= self.range and z.progress > best_prog:
                best_prog, best = z.progress, z
        return best

    def draw(self, surface, selected=False):
        cx, cy = self.x, self.y
        hs = GRID_SIZE // 2 - 3

        if self.ttype == "borrhammare":
            self._draw_borrhammare(surface, cx, cy, hs)
        elif self.ttype == "skrotare":
            self._draw_skrotare(surface, cx, cy, hs)
        elif self.ttype == "lhd":
            self._draw_lhd(surface, cx, cy, hs)
        elif self.ttype == "sprang":
            self._draw_sprang(surface, cx, cy, hs)

        if selected:
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), self.range, 1)

    def _draw_borrhammare(self, surface, cx, cy, hs):
        # Gul/svart maskin med borr
        pygame.draw.rect(surface, WARN_BLACK,   (cx - hs,     cy - hs,     hs * 2,     hs * 2))
        pygame.draw.rect(surface, WARN_YELLOW,  (cx - hs + 2, cy - hs + 2, hs * 2 - 4, hs * 2 - 4))
        # Borr (linje i riktning)
        bx = cx + int(math.cos(self.angle) * (hs + 10))
        by = cy + int(math.sin(self.angle) * (hs + 10))
        pygame.draw.line(surface, STEEL, (cx, cy), (bx, by), 5)
        pygame.draw.circle(surface, DARK_GRAY, (bx, by), 4)
        # LKAB-text-ish liten prick
        pygame.draw.circle(surface, LKAB_BLUE, (cx, cy), 4)

    def _draw_skrotare(self, surface, cx, cy, hs):
        # Blå hydraulisk arm
        pygame.draw.rect(surface, DARK_GRAY, (cx - hs, cy - hs, hs * 2, hs * 2))
        pygame.draw.rect(surface, (80, 130, 200), (cx - hs + 2, cy - hs + 2, hs * 2 - 4, hs * 2 - 4))
        # Arm
        ax = cx + int(math.cos(self.angle) * hs)
        ay = cy + int(math.sin(self.angle) * hs)
        pygame.draw.line(surface, STEEL, (cx, cy), (ax, ay), 6)
        # Skrotarskopa (liten rektangel vid spetsen)
        end_x = cx + int(math.cos(self.angle) * (hs + 8))
        end_y = cy + int(math.sin(self.angle) * (hs + 8))
        pygame.draw.circle(surface, GRAY, (end_x, end_y), 5)
        pygame.draw.circle(surface, WHITE, (cx, cy), 3)

    def _draw_lhd(self, surface, cx, cy, hs):
        # Orange gruvfordon (boxy)
        pygame.draw.rect(surface, WARN_BLACK, (cx - hs, cy - hs + 4, hs * 2, hs * 2 - 8))
        pygame.draw.rect(surface, ORANGE,    (cx - hs + 2, cy - hs + 6, hs * 2 - 4, hs * 2 - 12))
        # Hjul
        for dx, dy in [(-hs + 4, hs - 4), (hs - 4, hs - 4), (-hs + 4, -hs + 4), (hs - 4, -hs + 4)]:
            pygame.draw.circle(surface, DARK_GRAY, (cx + dx, cy + dy), 4)
            pygame.draw.circle(surface, GRAY,      (cx + dx, cy + dy), 2)
        # Skopa framåt
        sx = cx + int(math.cos(self.angle) * (hs + 4))
        sy = cy + int(math.sin(self.angle) * (hs + 4))
        pygame.draw.line(surface, STEEL, (cx, cy), (sx, sy), 7)

    def _draw_sprang(self, surface, cx, cy, hs):
        # Röd sprängstation med varningsränder
        for i in range(4):
            stripe = WARN_YELLOW if i % 2 == 0 else RED
            pygame.draw.rect(surface, stripe, (cx - hs + i * (hs // 2), cy - hs, hs // 2, hs * 2))
        # Cylindrisk sprängladdning
        pygame.draw.ellipse(surface, (180, 30, 30), (cx - hs // 2, cy - hs + 4, hs, hs * 2 - 8))
        # Tändkabel i riktning
        fuse_x = cx + int(math.cos(self.angle) * (hs + 6))
        fuse_y = cy + int(math.sin(self.angle) * (hs + 6))
        pygame.draw.line(surface, WARN_YELLOW, (cx, cy), (fuse_x, fuse_y), 2)
        pygame.draw.circle(surface, YELLOW, (fuse_x, fuse_y), 3)


class SplashEffect:
    def __init__(self, x, y, radius, is_explosion=False):
        self.x, self.y = x, y
        self.radius = radius
        self.timer = 25
        self.max_timer = 25
        self.is_explosion = is_explosion

    def update(self):
        self.timer -= 1

    def draw(self, surface):
        frac = self.timer / self.max_timer
        r = int(self.radius * (1 - frac) + 6)
        if self.is_explosion:
            col = (255, int(180 * frac), 0)
            pygame.draw.circle(surface, col, (int(self.x), int(self.y)), r, 3)
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), max(1, r - 4), 2)
        else:
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), r, 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("LKAB Gruvförsvar – Zombie Edition")
        self.clock = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 18)
        self.font_small = pygame.font.SysFont("Arial", 13)
        self.rng = random.Random(42)
        self.bg_surface = make_mine_background(self.rng)
        self.reset()

    def reset(self):
        self.towers = []
        self.zombies = []
        self.bullets = []
        self.effects = []
        self.money = 200
        self.lives = 20
        self.score = 0
        self.wave = 0
        self.wave_active = False
        self.spawn_queue = []
        self.spawn_timer = 0
        self.selected_tower_type = list(TOWER_TYPES.keys())[0]
        self.selected_tower = None
        self.game_over = False
        self.victory = False
        self.between_waves = True
        self.wave_complete_timer = 0
        self.all_waves_done = False

    def start_wave(self):
        if self.wave >= len(ZOMBIE_WAVES):
            self.all_waves_done = True
            return
        self.wave_active = True
        self.between_waves = False
        self.spawn_queue = []
        for group in ZOMBIE_WAVES[self.wave]:
            for _ in range(group["count"]):
                self.spawn_queue.append((group["type"], group["interval"]))
        self.spawn_timer = 0
        self.wave += 1

    def handle_spawn(self):
        if not self.wave_active or not self.spawn_queue:
            if self.wave_active and not self.spawn_queue and not self.zombies:
                self.wave_active = False
                self.between_waves = True
                self.wave_complete_timer = 120
                self.money += 50
            return
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            ztype, interval = self.spawn_queue.pop(0)
            self.zombies.append(Zombie(ztype))
            self.spawn_timer = interval

    def grid_occupied(self, col, row):
        if (col, row) in PATH_CELLS:
            return True
        if col < 0 or col >= COLS or row < 0 or row >= ROWS:
            return True
        return any(t.col == col and t.row == row for t in self.towers)

    def place_tower(self, col, row):
        tdata = TOWER_TYPES[self.selected_tower_type]
        if self.money < tdata["cost"] or self.grid_occupied(col, row):
            return
        self.towers.append(Tower(col, row, self.selected_tower_type))
        self.money -= tdata["cost"]

    def update(self):
        if self.game_over or self.victory:
            return
        self.handle_spawn()
        for z in self.zombies:
            z.update()
        for z in self.zombies:
            if z.reached_end:
                self.lives -= 1
        self.zombies = [z for z in self.zombies if z.alive and not z.reached_end]
        for t in self.towers:
            t.update(self.zombies, self.bullets)
        for b in self.bullets:
            b.update(self.zombies)
            if b.splash > 0 and not b.alive:
                self.effects.append(SplashEffect(b.x, b.y, b.splash,
                                                  is_explosion=(b.splash >= 50)))
        self.bullets = [b for b in self.bullets if b.alive]
        dead = [z for z in self.zombies if not z.alive]
        for z in dead:
            self.money += z.reward
            self.score += z.reward
        self.zombies = [z for z in self.zombies if z.alive]
        for e in self.effects:
            e.update()
        self.effects = [e for e in self.effects if e.timer > 0]
        if self.wave_complete_timer > 0:
            self.wave_complete_timer -= 1
        if self.lives <= 0:
            self.game_over = True
        if self.all_waves_done and not self.zombies and not self.wave_active:
            self.victory = True

    def draw_map(self):
        self.screen.blit(self.bg_surface, (0, 0))

        # Tunnel-gång markering (tunnelväggar)
        for c, r in PATH_CELLS:
            # Ljus markning längs kanten av tunneln
            x, y = c * GRID_SIZE, r * GRID_SIZE
            # Kolla grannarna – om grannen inte är en tunnel, rita en väggmarginal
            for nc, nr, side in [(c-1,r,'L'),(c+1,r,'R'),(c,r-1,'T'),(c,r+1,'B')]:
                if (nc, nr) not in PATH_CELLS:
                    if side == 'L':
                        pygame.draw.line(self.screen, (100, 88, 70), (x, y), (x, y + GRID_SIZE), 2)
                    elif side == 'R':
                        pygame.draw.line(self.screen, (100, 88, 70), (x + GRID_SIZE, y), (x + GRID_SIZE, y + GRID_SIZE), 2)
                    elif side == 'T':
                        pygame.draw.line(self.screen, (100, 88, 70), (x, y), (x + GRID_SIZE, y), 2)
                    elif side == 'B':
                        pygame.draw.line(self.screen, (100, 88, 70), (x, y + GRID_SIZE), (x + GRID_SIZE, y + GRID_SIZE), 2)

        # Start/mål-labels
        font = self.font_small
        sx, sy = grid_to_px(*WAYPOINTS[0])
        ex, ey = grid_to_px(*WAYPOINTS[-1])
        s = font.render("INGÅNG", True, BLACK)
        self.screen.blit(s, (sx - s.get_width() // 2, sy - 7))
        e = font.render("UTGÅNG", True, BLACK)
        self.screen.blit(e, (ex - e.get_width() // 2, ey - 7))

    def draw_ui(self):
        ui_y = ROWS * GRID_SIZE
        pygame.draw.rect(self.screen, UI_BG, (0, ui_y, SCREEN_W, SCREEN_H - ui_y))
        pygame.draw.line(self.screen, UI_LINE, (0, ui_y), (SCREEN_W, ui_y), 2)

        # Stats-rad
        self.screen.blit(self.font_big.render(f"Liv: {self.lives}", True, RED),         (10,  ui_y + 8))
        self.screen.blit(self.font_big.render(f"{self.money} kr",   True, YELLOW),      (140, ui_y + 8))
        self.screen.blit(self.font_big.render(f"Våg: {self.wave}/{len(ZOMBIE_WAVES)}", True, WHITE),  (295, ui_y + 8))
        self.screen.blit(self.font_big.render(f"Poäng: {self.score}", True, LIGHT_YELLOW), (445, ui_y + 8))

        # Tornknappar
        btn_x = 640
        for ttype, data in TOWER_TYPES.items():
            affordable = self.money >= data["cost"]
            selected   = self.selected_tower_type == ttype
            bg_col   = (40, 34, 28) if affordable else (28, 24, 22)
            bdr_col  = WARN_YELLOW if selected else (UI_LINE if affordable else DARK_GRAY)
            pygame.draw.rect(self.screen, bg_col,  (btn_x,     ui_y + 5,  94, 52))
            pygame.draw.rect(self.screen, bdr_col, (btn_x,     ui_y + 5,  94, 52), 2)
            # Tornfärg-chip
            pygame.draw.rect(self.screen, data["color"], (btn_x + 4, ui_y + 9, 12, 12))
            name = self.font_small.render(data["name"], True, WHITE if affordable else GRAY)
            cost = self.font_small.render(f"{data['cost']} kr", True, YELLOW if affordable else RED)
            self.screen.blit(name, (btn_x + 20, ui_y + 10))
            self.screen.blit(cost, (btn_x + 20, ui_y + 28))
            btn_x += 97

    def draw_ui_bottom(self):
        ui_y = ROWS * GRID_SIZE

        # Vågknapp
        if self.between_waves and not self.all_waves_done:
            if self.wave_complete_timer > 0:
                label = f"+50 kr! Nästa våg snart..."
            elif self.wave < len(ZOMBIE_WAVES):
                label = f"► Starta Våg {self.wave + 1}"
            else:
                label = "► Sista vågen!"
            btn = pygame.Rect(10, ui_y + 65, 215, 38)
            pygame.draw.rect(self.screen, (20, 80, 20), btn)
            pygame.draw.rect(self.screen, GREEN, btn, 2)
            t = self.font_med.render(label, True, WHITE)
            self.screen.blit(t, (btn.x + btn.w // 2 - t.get_width() // 2, btn.y + 9))

        # Vald torn info / beskrivning
        if self.selected_tower:
            t = self.selected_tower
            d = TOWER_TYPES[t.ttype]
            info = f"{d['name']}  |  Räckvidd: {t.range}  |  Skada: {t.damage}  |  {d['desc']}"
            self.screen.blit(self.font_small.render(info, True, LIGHT_YELLOW), (240, ui_y + 70))
        else:
            d = TOWER_TYPES[self.selected_tower_type]
            info = f"Valt: {d['name']}  –  {d['desc']}"
            self.screen.blit(self.font_small.render(info, True, GRAY), (240, ui_y + 70))

        # Kontroll-hint
        hint = self.font_small.render("[1-4] Välj maskin   [Klicka] Placera   [R] Starta om", True, DARK_GRAY)
        self.screen.blit(hint, (SCREEN_W - hint.get_width() - 8, ui_y + 70))

    def draw_overlay(self):
        if self.game_over:
            self._draw_message("GRUVAN FÖRLORAD", f"Poäng: {self.score}  –  Tryck R för att starta om", RED)
        elif self.victory:
            self._draw_message("GRUVAN SÄKRAD!", f"Alla vågor klarade! Poäng: {self.score}  –  Tryck R", YELLOW)

    def _draw_message(self, title, sub, color):
        overlay = pygame.Surface((SCREEN_W, ROWS * GRID_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))
        t = self.font_big.render(title, True, color)
        s = self.font_med.render(sub,   True, WHITE)
        self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, ROWS * GRID_SIZE // 2 - 30))
        self.screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, ROWS * GRID_SIZE // 2 + 10))

    def get_tower_btn_rect(self, idx):
        return pygame.Rect(640 + idx * 97, ROWS * GRID_SIZE + 5, 94, 52)

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                    keys = list(TOWER_TYPES.keys())
                    for i, k in enumerate([pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]):
                        if event.key == k and i < len(keys):
                            self.selected_tower_type = keys[i]
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    handled = False
                    for i in range(len(TOWER_TYPES)):
                        if self.get_tower_btn_rect(i).collidepoint(mx, my):
                            self.selected_tower_type = list(TOWER_TYPES.keys())[i]
                            handled = True
                            break
                    if not handled:
                        ui_y = ROWS * GRID_SIZE
                        wave_btn = pygame.Rect(10, ui_y + 65, 215, 38)
                        if wave_btn.collidepoint(mx, my) and self.between_waves and self.wave_complete_timer == 0:
                            self.start_wave()
                        elif my < ROWS * GRID_SIZE:
                            col, row = px_to_grid(mx, my)
                            clicked = next((t for t in self.towers if t.col == col and t.row == row), None)
                            if clicked:
                                self.selected_tower = clicked if self.selected_tower != clicked else None
                            else:
                                self.selected_tower = None
                                if not self.game_over:
                                    self.place_tower(col, row)

            self.update()
            self.draw_map()

            # Räckviddsförhandsvisning vid hover
            if my < ROWS * GRID_SIZE:
                col, row = px_to_grid(mx, my)
                if not self.grid_occupied(col, row):
                    px2, py2 = grid_to_px(col, row)
                    tdata = TOWER_TYPES[self.selected_tower_type]
                    pygame.draw.circle(self.screen, (200, 200, 200), (px2, py2), tdata["range"], 1)
                    col_hint = tdata["color"] if self.money >= tdata["cost"] else DARK_GRAY
                    pygame.draw.rect(self.screen, col_hint,
                                     (col * GRID_SIZE + 3, row * GRID_SIZE + 3, GRID_SIZE - 6, GRID_SIZE - 6), 2)

            for t in self.towers:
                t.draw(self.screen, selected=(self.selected_tower == t))
            for e in self.effects:
                e.draw(self.screen)
            for b in self.bullets:
                b.draw(self.screen)
            for z in self.zombies:
                z.draw(self.screen)

            self.draw_ui()
            self.draw_ui_bottom()
            self.draw_overlay()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
