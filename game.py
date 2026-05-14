import pygame
import math
import random

pygame.init()

SCREEN_W, SCREEN_H = 1024, 768
GRID_SIZE = 48
COLS = SCREEN_W // GRID_SIZE   # 21
ROWS = (SCREEN_H - 144) // GRID_SIZE  # 13

# --- Gruvfärger ---
ROCK_BG      = (28, 24, 22)
ROCK_WALL    = (45, 38, 32)
ROCK_LINE    = (38, 32, 28)
ORE_COLOR    = (140, 60, 30)
ORE_VEIN     = (180, 90, 40)
TUNNEL_FLOOR = (75, 65, 55)
TUNNEL_EDGE  = (55, 48, 40)
UI_BG        = (18, 15, 12)
UI_LINE      = (80, 65, 50)
WHITE        = (255, 255, 255)
BLACK        = (0, 0, 0)
RED          = (220, 50, 50)
YELLOW       = (255, 210, 30)
LKAB_BLUE    = (0, 60, 140)
ORANGE       = (255, 130, 0)
WARN_YELLOW  = (255, 200, 0)
WARN_BLACK   = (30, 30, 30)
GRAY         = (110, 100, 90)
DARK_GRAY    = (55, 50, 45)
STEEL        = (140, 150, 160)
LIGHT_YELLOW = (255, 230, 100)
GREEN        = (60, 200, 60)
DARK_GREEN   = (20, 120, 20)
PURPLE       = (160, 40, 200)
TEAL         = (40, 180, 160)

# ── Banor per nivå ──────────────────────────────────────────────────────────
LEVEL_WAYPOINTS = {
    1: [
        (0, 2), (4, 2), (4, 6), (8, 6), (8, 2), (12, 2),
        (12, 10), (16, 10), (16, 6), (20, 6), (20, 12)
    ],
    # Nivå 2 – mer vindlande, fler svängar
    2: [
        (0, 1), (3, 1), (3, 4), (6, 4), (6, 1), (9, 1),
        (9, 6), (5, 6), (5, 10), (9, 10), (9, 7),
        (13, 7), (13, 10), (17, 10), (17, 5), (20, 5), (20, 12)
    ],
}

LEVEL_NAMES = {
    1: "Gruvschakt 1 – Ingångsorten",
    2: "Gruvschakt 2 – Djupnivå",
}

# ── Torn ────────────────────────────────────────────────────────────────────
# unlock_wave = antal avklarade vågor som krävs (totalt, inte per nivå)
TOWER_TYPES = {
    "borrhammare": {
        "name": "Borrhammare", "cost": 100,  "unlock_wave": 0,
        "color": (200, 170, 50), "range": 110,
        "damage": 10, "fire_rate": 24,
        "bullet_color": (220, 200, 80), "bullet_speed": 7,
        "splash": 0, "slow": 0,
        "desc": "Snabb borrning, kort räckvidd",
    },
    "skrotare": {
        "name": "Skrotare", "cost": 175, "unlock_wave": 0,
        "color": (80, 130, 200), "range": 130,
        "damage": 16, "fire_rate": 45,
        "bullet_color": (120, 180, 255), "bullet_speed": 5,
        "splash": 0, "slow": 30,          # halverad från 70 → 30 bildrutor
        "desc": "Saktar ner något, medellång räckvidd",
    },
    "lhd": {
        "name": "LHD", "cost": 275, "unlock_wave": 3,
        "color": ORANGE, "range": 105,
        "damage": 42, "fire_rate": 70,
        "bullet_color": (255, 160, 40), "bullet_speed": 5,
        "splash": 40, "slow": 0,
        "desc": "Skopsprängning, träffar flera",
    },
    "sprang": {
        "name": "Sprängare", "cost": 250, "unlock_wave": 3,
        "color": (210, 40, 40), "range": 140,
        "damage": 72, "fire_rate": 120,
        "bullet_color": (255, 80, 40), "bullet_speed": 4,
        "splash": 60, "slow": 0,
        "desc": "Stor explosion, lång räckvidd",
    },
    "malmkross": {
        "name": "Malmkross", "cost": 425, "unlock_wave": 5,
        "color": (120, 100, 75), "range": 95,
        "damage": 60, "fire_rate": 55,
        "bullet_color": (180, 150, 100), "bullet_speed": 4,
        "splash": 35, "slow": 25,
        "desc": "Krossar + saktar lite, kort räckvidd",
    },
    "detonator": {
        "name": "Detonator", "cost": 625, "unlock_wave": 7,
        "color": (200, 20, 20), "range": 165,
        "damage": 168, "fire_rate": 160,
        "bullet_color": (255, 80, 20), "bullet_speed": 3,
        "splash": 95, "slow": 0,
        "desc": "Massiv explosion, lång räckvidd",
    },
}

# ── Fiender ─────────────────────────────────────────────────────────────────
# HP och speed skalas med game.hp_scale / game.speed_scale vid spawn
ZOMBIE_STATS = {
    "normal":   {"hp": 70,   "speed": 1.2,  "reward": 10,  "color": (80,  170, 80),  "size": 10},
    "fast":     {"hp": 45,   "speed": 2.4,  "reward": 15,  "color": (200, 200, 50),  "size": 8},
    "tank":     {"hp": 275,  "speed": 0.75, "reward": 30,  "color": (180, 80,  80),  "size": 14},
    "boss":     {"hp": 700,  "speed": 0.55, "reward": 80,  "color": (200, 50,  200), "size": 20},
    "megaboss": {"hp": 3500, "speed": 0.32, "reward": 500, "color": (130, 0,   160), "size": 30},
    # Nivå 2 – nya fiender
    "rusher":   {"hp": 20,   "speed": 4.2,  "reward": 18,  "color": (255, 220, 60),  "size": 7},
    "bergtroll":{"hp": 450,  "speed": 0.55, "reward": 60,  "color": (130, 100, 65),  "size": 17},
}

def _w(count, interval, ztype):
    return [{"type": ztype, "count": count, "interval": interval}]

LEVEL_WAVES = {
    1: [
        _w(8,  60, "normal"),
        _w(12, 50, "normal") + _w(5,  40, "fast"),
        _w(10, 45, "normal") + _w(8,  35, "fast")  + _w(2, 80, "tank"),
        _w(15, 40, "fast")   + _w(5,  70, "tank"),
        _w(20, 40, "normal") + _w(10, 32, "fast")  + _w(8,  65, "tank"),
        _w(25, 35, "normal") + _w(12, 28, "fast")  + _w(10, 55, "tank") + _w(3, 90, "boss"),
        _w(15, 30, "fast")   + _w(12, 50, "tank")  + _w(5,  80, "boss"),
        _w(30, 28, "normal") + _w(18, 25, "fast")  + _w(14, 45, "tank") + _w(6, 70, "boss"),
        _w(20, 25, "fast")   + _w(18, 40, "tank")  + _w(10, 60, "boss"),
        _w(15, 28, "fast")   + _w(10, 45, "tank")  + _w(6,  60, "boss") + _w(1, 1, "megaboss"),
    ],
    2: [
        _w(12, 50, "normal") + _w(10, 25, "rusher"),
        _w(15, 40, "fast")   + _w(15, 20, "rusher"),
        _w(10, 45, "normal") + _w(12, 35, "fast")  + _w(4,  70, "bergtroll"),
        _w(25, 22, "rusher") + _w(6,  65, "bergtroll"),
        _w(20, 35, "fast")   + _w(8,  60, "bergtroll") + _w(3, 90, "boss"),
        _w(20, 28, "normal") + _w(20, 18, "rusher") + _w(8,  55, "bergtroll") + _w(4, 80, "boss"),
        _w(25, 22, "fast")   + _w(10, 50, "bergtroll") + _w(7,  70, "boss"),
        _w(35, 18, "rusher") + _w(12, 45, "bergtroll") + _w(9,  60, "boss"),
        _w(25, 20, "fast")   + _w(15, 40, "bergtroll") + _w(12, 55, "boss"),
        _w(20, 18, "rusher") + _w(12, 42, "bergtroll") + _w(8,  55, "boss") + _w(1, 1, "megaboss"),
    ],
}

UNLOCK_MESSAGES = {3: "LHD och Sprängare upplåsta!", 5: "Malmkross upplåst!", 7: "Detonator upplåst!"}

# ── Hjälpfunktioner ─────────────────────────────────────────────────────────
def grid_to_px(col, row):
    return col * GRID_SIZE + GRID_SIZE // 2, row * GRID_SIZE + GRID_SIZE // 2

def px_to_grid(x, y):
    return x // GRID_SIZE, y // GRID_SIZE

def build_path_cells(waypoints):
    cells = set()
    for i in range(len(waypoints) - 1):
        c1, r1 = waypoints[i]
        c2, r2 = waypoints[i + 1]
        dc = (1 if c2 > c1 else -1) if c2 != c1 else 0
        dr = (1 if r2 > r1 else -1) if r2 != r1 else 0
        c, r = c1, r1
        while (c, r) != (c2, r2):
            cells.add((c, r))
            c += dc
            r += dr
        cells.add((c2, r2))
    return cells

def make_mine_background(rng, path_cells, level=1):
    surf = pygame.Surface((SCREEN_W, ROWS * GRID_SIZE))
    # Djupare, mörkare på nivå 2
    bg = ROCK_BG if level == 1 else (20, 16, 14)
    wall = ROCK_WALL if level == 1 else (38, 30, 24)
    surf.fill(bg)
    for c in range(COLS):
        for r in range(ROWS):
            x, y = c * GRID_SIZE, r * GRID_SIZE
            if (c, r) not in path_cells:
                shade = rng.randint(-10, 10)
                col = tuple(max(0, min(255, v + shade)) for v in wall)
                pygame.draw.rect(surf, col, (x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2))
    # Malmådror (fler och rödare på djupnivå)
    vein_col = ORE_VEIN if level == 1 else (200, 80, 20)
    ore_col  = ORE_COLOR if level == 1 else (160, 50, 10)
    for _ in range(28 + level * 10):
        cx2 = rng.randint(0, SCREEN_W)
        cy2 = rng.randint(0, ROWS * GRID_SIZE)
        gc, gr = px_to_grid(cx2, cy2)
        if (gc, gr) in path_cells:
            continue
        length = rng.randint(20, 80)
        angle  = rng.uniform(0, math.pi * 2)
        ex = int(cx2 + math.cos(angle) * length)
        ey = int(cy2 + math.sin(angle) * length)
        pygame.draw.line(surf, vein_col, (cx2, cy2), (ex, ey), rng.randint(1, 3))
        for _ in range(rng.randint(2, 5)):
            bx = cx2 + rng.randint(-12, 12)
            by = cy2 + rng.randint(-12, 12)
            pygame.draw.circle(surf, ore_col, (bx, by), rng.randint(2, 5))
    for _ in range(60 + level * 20):
        sx = rng.randint(0, SCREEN_W)
        sy = rng.randint(0, ROWS * GRID_SIZE)
        gc, gr = px_to_grid(sx, sy)
        if (gc, gr) in path_cells:
            continue
        pts = [(sx, sy)]
        for _ in range(rng.randint(2, 5)):
            lx, ly = pts[-1]
            pts.append((lx + rng.randint(-14, 14), ly + rng.randint(-14, 14)))
        for i in range(len(pts) - 1):
            pygame.draw.line(surf, ROCK_LINE, pts[i], pts[i + 1], 1)
    for c, r in path_cells:
        x, y = c * GRID_SIZE, r * GRID_SIZE
        floor = TUNNEL_FLOOR if level == 1 else (60, 50, 42)
        pygame.draw.rect(surf, floor, (x, y, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surf, TUNNEL_EDGE, (x, y, GRID_SIZE, GRID_SIZE), 1)
        for _ in range(4):
            gx = x + rng.randint(4, GRID_SIZE - 4)
            gy = y + rng.randint(4, GRID_SIZE - 4)
            pygame.draw.circle(surf, TUNNEL_EDGE, (gx, gy), 1)
    for c in range(COLS + 1):
        pygame.draw.line(surf, ROCK_LINE, (c * GRID_SIZE, 0), (c * GRID_SIZE, ROWS * GRID_SIZE), 1)
    for r in range(ROWS + 1):
        pygame.draw.line(surf, ROCK_LINE, (0, r * GRID_SIZE), (SCREEN_W, r * GRID_SIZE), 1)
    # Varningsränder ingång/utgång
    for wp in [LEVEL_WAYPOINTS[level][0], LEVEL_WAYPOINTS[level][-1]]:
        wx, wy = wp[0] * GRID_SIZE, wp[1] * GRID_SIZE
        for i in range(4):
            stripe_col = WARN_YELLOW if i % 2 == 0 else WARN_BLACK
            pygame.draw.rect(surf, stripe_col, (wx + i * (GRID_SIZE // 4), wy, GRID_SIZE // 4, GRID_SIZE))
    return surf

# ── Klasser ──────────────────────────────────────────────────────────────────
class Zombie:
    def __init__(self, ztype, hp_scale=1.0, speed_scale=1.0):
        stats = ZOMBIE_STATS[ztype]
        self.ztype      = ztype
        self.max_hp     = int(stats["hp"] * hp_scale)
        self.hp         = self.max_hp
        self.base_speed = stats["speed"] * speed_scale
        self.speed      = self.base_speed
        self.reward     = stats["reward"]
        self.color      = stats["color"]
        self.size       = stats["size"]
        self.waypoint_idx = 0
        self._waypoints = None   # sätts av Game
        px2, py2 = 0, 0         # sätts av Game efter skapande
        self.x = float(px2)
        self.y = float(py2)
        self.alive       = True
        self.reached_end = False
        self.slow_timer  = 0
        self.progress    = 0.0

    def set_waypoints(self, waypoints):
        self._waypoints = waypoints
        px2, py2 = grid_to_px(*waypoints[0])
        self.x = float(px2)
        self.y = float(py2)

    def update(self):
        if self.slow_timer > 0:
            self.slow_timer -= 1
            self.speed = self.base_speed * 0.55   # mjukare bromsa
        else:
            self.speed = self.base_speed
        if self.waypoint_idx + 1 >= len(self._waypoints):
            self.reached_end = True
            self.alive = False
            return
        tx, ty = grid_to_px(*self._waypoints[self.waypoint_idx + 1])
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
        if self.ztype == "megaboss":
            self._draw_megaboss(surface, cx, cy)
            return
        if self.ztype == "rusher":
            self._draw_rusher(surface, cx, cy)
            return
        if self.ztype == "bergtroll":
            self._draw_bergtroll(surface, cx, cy)
            return
        self._draw_standard(surface, cx, cy)

    def _draw_standard(self, surface, cx, cy):
        s = self.size
        pygame.draw.circle(surface, (0, 0, 0), (cx + 2, cy + 2), s)
        pygame.draw.circle(surface, self.color, (cx, cy), s)
        helmet_col = (220, 180, 30) if self.ztype not in ("boss",) else (200, 30, 200)
        pygame.draw.arc(surface, helmet_col,
                        (cx - s, cy - s - 2, s * 2, s + 2), 0, math.pi, 3)
        pygame.draw.circle(surface, YELLOW, (cx, cy - s + 1), 2)
        eye_off = max(2, s // 3)
        for ex2, sign in [(cx - eye_off, 1), (cx + eye_off, 1)]:
            pygame.draw.circle(surface, WHITE,   (ex2, cy - 2), 3)
            pygame.draw.circle(surface, BLACK,   (ex2 + 1, cy - 2), 1)
        self._draw_hp_bar(surface, cx, cy, s)
        if self.slow_timer > 0:
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), s + 3, 2)

    def _draw_rusher(self, surface, cx, cy):
        s = self.size
        # Liten, gul, sylvass
        pygame.draw.circle(surface, (0, 0, 0), (cx + 1, cy + 1), s)
        pygame.draw.circle(surface, self.color, (cx, cy), s)
        # Spetsig "hjälm"
        pygame.draw.polygon(surface, (255, 180, 0),
                            [(cx, cy - s - 4), (cx - 3, cy - s + 1), (cx + 3, cy - s + 1)])
        eye_off = 2
        pygame.draw.circle(surface, RED, (cx - eye_off, cy - 1), 2)
        pygame.draw.circle(surface, RED, (cx + eye_off, cy - 1), 2)
        self._draw_hp_bar(surface, cx, cy, s)
        if self.slow_timer > 0:
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), s + 2, 1)

    def _draw_bergtroll(self, surface, cx, cy):
        s = self.size
        # Stor, stenbrun, klumpig
        pygame.draw.circle(surface, (0, 0, 0), (cx + 3, cy + 3), s)
        pygame.draw.circle(surface, self.color, (cx, cy), s)
        # Stenig textur – mörka fläckar
        for dx2, dy2, r2 in [(-5, -3, 3), (4, -5, 2), (-3, 4, 2), (5, 3, 3)]:
            pygame.draw.circle(surface, (100, 75, 45), (cx + dx2, cy + dy2), r2)
        # Gröna ögon
        eye_off = s // 3
        pygame.draw.circle(surface, (50, 220, 50), (cx - eye_off, cy - 3), 4)
        pygame.draw.circle(surface, (50, 220, 50), (cx + eye_off, cy - 3), 4)
        pygame.draw.circle(surface, BLACK, (cx - eye_off + 1, cy - 3), 2)
        pygame.draw.circle(surface, BLACK, (cx + eye_off + 1, cy - 3), 2)
        self._draw_hp_bar(surface, cx, cy, s)
        if self.slow_timer > 0:
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), s + 3, 2)

    def _draw_megaboss(self, surface, cx, cy):
        s = self.size
        tick = pygame.time.get_ticks()
        glow_r = s + 8 + int(4 * math.sin(tick * 0.005))
        pygame.draw.circle(surface, (60, 0, 80), (cx, cy), glow_r)
        pygame.draw.circle(surface, (0, 0, 0),  (cx + 3, cy + 3), s)
        pygame.draw.circle(surface, self.color, (cx, cy), s)
        pygame.draw.circle(surface, (200, 100, 255), (cx, cy), s, 3)
        pygame.draw.arc(surface, (180, 0, 180),
                        (cx - s, cy - s - 4, s * 2, s + 4), 0, math.pi, 5)
        pygame.draw.circle(surface, (255, 255, 100), (cx, cy - s + 2), 5)
        pygame.draw.circle(surface, WHITE, (cx, cy - s + 2), 3)
        eye_off = s // 3
        for ex2 in [cx - eye_off, cx + eye_off]:
            pygame.draw.circle(surface, (255, 50, 50), (ex2, cy - 4), 5)
            pygame.draw.circle(surface, (255, 200, 0), (ex2, cy - 4), 2)
        for i in range(-s // 2, s // 2, 6):
            pygame.draw.line(surface, (255, 50, 50),
                             (cx + i, cy + s // 2), (cx + i + 3, cy + s // 2 + 5), 2)
        # Bred HP-bar
        bar_w = s * 3
        bar_x = cx - s - s // 2
        bar_y = cy - s - 14
        pygame.draw.rect(surface, (80, 0, 0), (bar_x, bar_y, bar_w, 6))
        pygame.draw.rect(surface, PURPLE,    (bar_x, bar_y, int(bar_w * self.hp / self.max_hp), 6))
        pygame.draw.rect(surface, WHITE,     (bar_x, bar_y, bar_w, 6), 1)

    def _draw_hp_bar(self, surface, cx, cy, s):
        bar_w = s * 2
        bar_x = cx - s
        bar_y = cy - s - 10
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_w, 4))
        pygame.draw.rect(surface, GREEN,     (bar_x, bar_y, int(bar_w * self.hp / self.max_hp), 4))


class Bullet:
    def __init__(self, x, y, target, speed, damage, color, splash, slow):
        self.x, self.y = float(x), float(y)
        self.target = target
        self.speed  = speed
        self.damage = damage
        self.color  = color
        self.splash = splash
        self.slow   = slow
        self.alive  = True

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
                        z.slow_timer = max(z.slow_timer, self.slow)
        else:
            self.target.hp -= self.damage
            if self.target.hp <= 0:
                self.target.alive = False
            if self.slow:
                self.target.slow_timer = max(self.target.slow_timer, self.slow)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, WHITE,      (int(self.x), int(self.y)), 2)


class Tower:
    def __init__(self, col, row, ttype):
        self.col, self.row = col, row
        self.ttype = ttype
        d = TOWER_TYPES[ttype]
        self.color        = d["color"]
        self.range        = d["range"]
        self.damage       = d["damage"]
        self.fire_rate    = d["fire_rate"]
        self.bullet_color = d["bullet_color"]
        self.bullet_speed = d["bullet_speed"]
        self.splash       = d["splash"]
        self.slow         = d["slow"]
        self.cooldown     = 0
        self.x, self.y   = grid_to_px(col, row)
        self.angle        = 0.0

    def update(self, zombies, bullets):
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        target = self._find_target(zombies)
        if target:
            self.angle = math.atan2(target.y - self.y, target.x - self.x)
            bullets.append(Bullet(self.x, self.y, target,
                                  self.bullet_speed, self.damage,
                                  self.bullet_color, self.splash, self.slow))
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
        draw_fn = {
            "borrhammare": self._draw_borrhammare,
            "skrotare":    self._draw_skrotare,
            "lhd":         self._draw_lhd,
            "sprang":      self._draw_sprang,
            "malmkross":   self._draw_malmkross,
            "detonator":   self._draw_detonator,
        }
        draw_fn[self.ttype](surface, cx, cy, hs)
        if selected:
            pygame.draw.circle(surface, WHITE, (cx, cy), self.range, 1)

    def _draw_borrhammare(self, s, cx, cy, hs):
        pygame.draw.rect(s, WARN_BLACK,  (cx-hs, cy-hs, hs*2, hs*2))
        pygame.draw.rect(s, WARN_YELLOW, (cx-hs+2, cy-hs+2, hs*2-4, hs*2-4))
        bx = cx + int(math.cos(self.angle)*(hs+10))
        by = cy + int(math.sin(self.angle)*(hs+10))
        pygame.draw.line(s, STEEL, (cx,cy), (bx,by), 5)
        pygame.draw.circle(s, DARK_GRAY, (bx,by), 4)
        pygame.draw.circle(s, LKAB_BLUE, (cx,cy), 4)

    def _draw_skrotare(self, s, cx, cy, hs):
        pygame.draw.rect(s, DARK_GRAY,      (cx-hs, cy-hs, hs*2, hs*2))
        pygame.draw.rect(s, (80,130,200),   (cx-hs+2, cy-hs+2, hs*2-4, hs*2-4))
        ax = cx + int(math.cos(self.angle)*hs)
        ay = cy + int(math.sin(self.angle)*hs)
        pygame.draw.line(s, STEEL, (cx,cy), (ax,ay), 6)
        ex2 = cx + int(math.cos(self.angle)*(hs+8))
        ey2 = cy + int(math.sin(self.angle)*(hs+8))
        pygame.draw.circle(s, GRAY, (ex2,ey2), 5)
        pygame.draw.circle(s, WHITE, (cx,cy), 3)

    def _draw_lhd(self, s, cx, cy, hs):
        pygame.draw.rect(s, WARN_BLACK, (cx-hs, cy-hs+4, hs*2, hs*2-8))
        pygame.draw.rect(s, ORANGE,    (cx-hs+2, cy-hs+6, hs*2-4, hs*2-12))
        for dx2,dy2 in [(-hs+4,hs-4),(hs-4,hs-4),(-hs+4,-hs+4),(hs-4,-hs+4)]:
            pygame.draw.circle(s, DARK_GRAY, (cx+dx2,cy+dy2), 4)
            pygame.draw.circle(s, GRAY,      (cx+dx2,cy+dy2), 2)
        sx2 = cx+int(math.cos(self.angle)*(hs+4))
        sy2 = cy+int(math.sin(self.angle)*(hs+4))
        pygame.draw.line(s, STEEL, (cx,cy), (sx2,sy2), 7)

    def _draw_sprang(self, s, cx, cy, hs):
        for i in range(4):
            stripe = WARN_YELLOW if i % 2 == 0 else RED
            pygame.draw.rect(s, stripe, (cx-hs+i*(hs//2), cy-hs, hs//2, hs*2))
        pygame.draw.ellipse(s, (180,30,30), (cx-hs//2, cy-hs+4, hs, hs*2-8))
        fx = cx+int(math.cos(self.angle)*(hs+6))
        fy = cy+int(math.sin(self.angle)*(hs+6))
        pygame.draw.line(s, WARN_YELLOW, (cx,cy), (fx,fy), 2)
        pygame.draw.circle(s, YELLOW, (fx,fy), 3)

    def _draw_malmkross(self, s, cx, cy, hs):
        pygame.draw.rect(s, (60,50,40),  (cx-hs, cy-hs, hs*2, hs*2))
        pygame.draw.rect(s, (120,100,75),(cx-hs+2, cy-hs+2, hs*2-4, hs*2-4))
        ax = cx+int(math.cos(self.angle)*(hs+6))
        ay = cy+int(math.sin(self.angle)*(hs+6))
        pygame.draw.line(s, (80,65,50), (cx,cy), (ax,ay), 8)
        pygame.draw.rect(s, (90,75,60),   (ax-6, ay-6, 12, 12))
        pygame.draw.rect(s, WARN_YELLOW,  (ax-6, ay-6, 12, 12), 1)
        pygame.draw.circle(s, (160,130,90), (cx,cy), 4)

    def _draw_detonator(self, s, cx, cy, hs):
        pygame.draw.rect(s, (80,0,0),   (cx-hs, cy-hs, hs*2, hs*2))
        pygame.draw.rect(s, (200,20,20),(cx-hs+2, cy-hs+2, hs*2-4, hs*2-4))
        for i, bx2 in enumerate([cx-8, cx, cx+8]):
            col = WARN_YELLOW if (pygame.time.get_ticks()//200+i)%3 == 0 else (160,160,0)
            pygame.draw.circle(s, col, (bx2, cy+4), 4)
        ex2 = cx+int(math.cos(self.angle)*(hs+8))
        ey2 = cy+int(math.sin(self.angle)*(hs+8))
        pygame.draw.line(s, WARN_YELLOW, (cx, cy-4), (ex2,ey2), 2)
        pygame.draw.circle(s, (255,120,50), (ex2,ey2), 4)


class SplashEffect:
    def __init__(self, x, y, radius, big=False):
        self.x, self.y = x, y
        self.radius    = radius
        self.timer     = 30 if big else 20
        self.max_timer = self.timer
        self.big       = big

    def update(self):
        self.timer -= 1

    def draw(self, surface):
        frac = self.timer / self.max_timer
        r = int(self.radius * (1 - frac) + 6)
        if self.big:
            col = (255, int(160 * frac), 0)
            pygame.draw.circle(surface, col,    (int(self.x), int(self.y)), r,           4)
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), max(1,r-6),  2)
        else:
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), r, 2)


class UnlockBanner:
    def __init__(self, text):
        self.text  = text
        self.timer = 180

    def draw(self, surface, font):
        if self.timer <= 0:
            return
        t = font.render(f"★  {self.text}  ★", True, WARN_YELLOW)
        x = SCREEN_W // 2 - t.get_width() // 2
        y = ROWS * GRID_SIZE // 2 - 20
        bg = pygame.Surface((t.get_width() + 20, t.get_height() + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, min(180, self.timer * 3)))
        surface.blit(bg, (x - 10, y - 5))
        surface.blit(t, (x, y))
        self.timer -= 1


# ── Spelet ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.screen     = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("MineBattle – LKAB Gruvförsvar")
        self.clock      = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 17)
        self.font_small = pygame.font.SysFont("Arial", 12)
        self.rng        = random.Random(42)
        self.level      = 1
        self._init_level()
        self.total_waves_done = 0   # för upplåsning av torn
        self.money = 200
        self.lives = 20
        self.score = 0
        self._reset_wave_state()

    def _init_level(self):
        self.waypoints  = LEVEL_WAYPOINTS[self.level]
        self.path_cells = build_path_cells(self.waypoints)
        self.bg_surface = make_mine_background(
            random.Random(self.level * 99), self.path_cells, self.level)

    def _reset_wave_state(self):
        self.towers      = []
        self.zombies     = []
        self.bullets     = []
        self.effects     = []
        self.banners     = []
        self.wave        = 0           # våg inom nivå (0..9)
        self.wave_active = False
        self.spawn_queue = []
        self.spawn_timer = 0
        self.selected_tower_type  = "borrhammare"
        self.selected_tower       = None
        self.game_over            = False
        self.between_waves        = True
        self.wave_complete_timer  = 0
        self.level_complete       = False
        self.level_transition     = False  # visar övergångsskärm

    def full_reset(self):
        self.level            = 1
        self.total_waves_done = 0
        self.money = 200
        self.lives = 20
        self.score = 0
        self._init_level()
        self._reset_wave_state()

    def begin_next_level(self):
        """Sälj tillbaka torn (70%), byt bana, behåll pengar/liv/poäng."""
        refund = sum(int(TOWER_TYPES[t.ttype]["cost"] * 0.7) for t in self.towers)
        self.money += refund
        self.level += 1
        self._init_level()
        self._reset_wave_state()
        self.level_transition = True   # visa övergångsskärm

    # ── Upplåsning ───────────────────────────────────────────────────────────
    def tower_unlocked(self, ttype):
        return self.total_waves_done >= TOWER_TYPES[ttype]["unlock_wave"]

    # ── Våghantering ─────────────────────────────────────────────────────────
    def _hp_scale(self):
        # Våg 1→1.1x, Våg 5→1.5x, Våg 10→2.0x. Nivå 2 börjar på 1.8x.
        return 1.0 + (self.level - 1) * 0.8 + self.wave * 0.10

    def _speed_scale(self):
        return 1.0 + (self.level - 1) * 0.08 + self.wave * 0.01

    def start_wave(self):
        waves = LEVEL_WAVES[self.level]
        if self.wave >= len(waves):
            return
        self.wave_active   = True
        self.between_waves = False
        self.spawn_queue   = []
        for group in waves[self.wave]:
            for _ in range(group["count"]):
                self.spawn_queue.append((group["type"], group["interval"]))
        self.spawn_timer = 0
        self.wave += 1

    def handle_spawn(self):
        if not self.wave_active or not self.spawn_queue:
            if self.wave_active and not self.spawn_queue and not self.zombies:
                self.wave_active  = False
                self.between_waves = True
                self.wave_complete_timer = 120
                bonus = 50 + self.wave * 10
                self.money += bonus
                self.total_waves_done += 1
                # Upplåsningsbanners
                if self.total_waves_done in UNLOCK_MESSAGES:
                    self.banners.append(UnlockBanner(UNLOCK_MESSAGES[self.total_waves_done]))
                # Nivå klar?
                if self.wave >= len(LEVEL_WAVES[self.level]):
                    self.level_complete = True
            return
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            ztype, interval = self.spawn_queue.pop(0)
            z = Zombie(ztype, self._hp_scale(), self._speed_scale())
            z.set_waypoints(self.waypoints)
            self.zombies.append(z)
            self.spawn_timer = interval

    def grid_occupied(self, col, row):
        if (col, row) in self.path_cells:
            return True
        if col < 0 or col >= COLS or row < 0 or row >= ROWS:
            return True
        return any(t.col == col and t.row == row for t in self.towers)

    def place_tower(self, col, row):
        tdata = TOWER_TYPES[self.selected_tower_type]
        if not self.tower_unlocked(self.selected_tower_type):
            return
        if self.money < tdata["cost"] or self.grid_occupied(col, row):
            return
        self.towers.append(Tower(col, row, self.selected_tower_type))
        self.money -= tdata["cost"]

    def update(self):
        if self.game_over or self.level_transition or self.level_complete:
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
                self.effects.append(SplashEffect(b.x, b.y, b.splash, big=(b.splash >= 80)))
        self.bullets = [b for b in self.bullets if b.alive]
        for z in [z for z in self.zombies if not z.alive]:
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

    # ── Ritning ───────────────────────────────────────────────────────────────
    def draw_map(self):
        self.screen.blit(self.bg_surface, (0, 0))
        for c, r in self.path_cells:
            x, y = c * GRID_SIZE, r * GRID_SIZE
            for nc, nr, side in [(c-1,r,'L'),(c+1,r,'R'),(c,r-1,'T'),(c,r+1,'B')]:
                if (nc, nr) not in self.path_cells:
                    wall = (100, 88, 70)
                    if   side == 'L': pygame.draw.line(self.screen, wall, (x, y),            (x, y+GRID_SIZE),            2)
                    elif side == 'R': pygame.draw.line(self.screen, wall, (x+GRID_SIZE, y),   (x+GRID_SIZE, y+GRID_SIZE),  2)
                    elif side == 'T': pygame.draw.line(self.screen, wall, (x, y),             (x+GRID_SIZE, y),            2)
                    elif side == 'B': pygame.draw.line(self.screen, wall, (x, y+GRID_SIZE),   (x+GRID_SIZE, y+GRID_SIZE),  2)
        sx, sy = grid_to_px(*self.waypoints[0])
        ex, ey = grid_to_px(*self.waypoints[-1])
        s = self.font_small.render("INGÅNG", True, BLACK)
        e = self.font_small.render("UTGÅNG", True, BLACK)
        self.screen.blit(s, (sx - s.get_width()//2, sy-7))
        self.screen.blit(e, (ex - e.get_width()//2, ey-7))

    def draw_boss_bar(self):
        mb = next((z for z in self.zombies if z.ztype == "megaboss"), None)
        if not mb:
            return
        bar_w = 500
        bar_x = SCREEN_W // 2 - bar_w // 2
        bar_y = 6
        pygame.draw.rect(self.screen, (40, 0, 50),  (bar_x-2, bar_y-2, bar_w+4, 18))
        pygame.draw.rect(self.screen, (80, 0, 0),   (bar_x, bar_y, bar_w, 14))
        pygame.draw.rect(self.screen, PURPLE,       (bar_x, bar_y, int(bar_w*mb.hp/mb.max_hp), 14))
        pygame.draw.rect(self.screen, WHITE,        (bar_x, bar_y, bar_w, 14), 1)
        lbl = self.font_small.render(f"☠  MEGA-BOSS  {mb.hp}/{mb.max_hp}", True, WHITE)
        self.screen.blit(lbl, (SCREEN_W//2 - lbl.get_width()//2, bar_y))

    def draw_ui(self):
        ui_y = ROWS * GRID_SIZE
        pygame.draw.rect(self.screen, UI_BG,   (0, ui_y, SCREEN_W, SCREEN_H-ui_y))
        pygame.draw.line(self.screen, UI_LINE,  (0, ui_y), (SCREEN_W, ui_y), 2)

        # Stats
        stats = [
            (f"Liv: {self.lives}", RED),
            (f"{self.money} kr",   YELLOW),
            (f"V{self.wave}/{len(LEVEL_WAVES[self.level])}  Niv.{self.level}", WHITE),
            (f"Poäng: {self.score}", LIGHT_YELLOW),
        ]
        sx2 = 8
        for text, col in stats:
            surf = self.font_big.render(text, True, col)
            self.screen.blit(surf, (sx2, ui_y + 6))
            sx2 += surf.get_width() + 16

        # Tornknappar (6 st, höger)
        btn_w  = 88
        btn_x0 = SCREEN_W - len(TOWER_TYPES) * btn_w - 4
        tower_list = list(TOWER_TYPES.keys())
        for i, (ttype, data) in enumerate(TOWER_TYPES.items()):
            bx = btn_x0 + i * btn_w
            by = ui_y + 4
            unlocked   = self.tower_unlocked(ttype)
            affordable = self.money >= data["cost"] and unlocked
            selected   = self.selected_tower_type == ttype
            bg_col  = (40, 34, 28) if unlocked else (22, 18, 16)
            bdr_col = WARN_YELLOW if selected else (UI_LINE if unlocked else DARK_GRAY)
            pygame.draw.rect(self.screen, bg_col,  (bx, by, btn_w, 58))
            pygame.draw.rect(self.screen, bdr_col, (bx, by, btn_w, 58), 2)
            if unlocked:
                pygame.draw.rect(self.screen, data["color"], (bx+4, by+5, 10, 10))
                self.screen.blit(self.font_small.render(data["name"], True, WHITE if affordable else GRAY), (bx+16, by+5))
                self.screen.blit(self.font_small.render(f"{data['cost']} kr", True, YELLOW if affordable else RED), (bx+16, by+22))
                self.screen.blit(self.font_small.render(f"[{i+1}]", True, GRAY), (bx+16, by+39))
            else:
                req = data["unlock_wave"]
                self.screen.blit(self.font_small.render(data["name"],           True, DARK_GRAY),    (bx+4, by+8))
                self.screen.blit(self.font_small.render(f"Lås upp V{req}", True, (100,80,60)), (bx+4, by+26))

        # Vågknapp
        if self.between_waves and not self.level_complete:
            if self.wave_complete_timer > 0:
                bonus = 50 + self.wave * 10
                label, btn_col = f"+{bonus} kr bonus!", (20, 60, 20)
            else:
                label = f"► Starta Våg {self.wave+1}"
                btn_col = (20, 80, 20) if self.wave < len(LEVEL_WAVES[self.level]) else (80, 20, 20)
            btn = pygame.Rect(8, ui_y+72, 210, 34)
            pygame.draw.rect(self.screen, btn_col, btn)
            pygame.draw.rect(self.screen, GREEN, btn, 2)
            t = self.font_med.render(label, True, WHITE)
            self.screen.blit(t, (btn.x + btn.w//2 - t.get_width()//2, btn.y+8))

        # Info
        if self.selected_tower:
            t2 = self.selected_tower
            d2 = TOWER_TYPES[t2.ttype]
            info = f"{d2['name']}  |  Räckvidd: {t2.range}  |  Skada: {t2.damage}  |  {d2['desc']}"
        else:
            d2 = TOWER_TYPES[self.selected_tower_type]
            info = f"Valt: {d2['name']}  –  {d2['desc']}"
        self.screen.blit(self.font_small.render(info, True, LIGHT_YELLOW if self.selected_tower else GRAY),
                         (225, ui_y+78))
        hint = self.font_small.render("[1-6] Välj maskin   [Klicka] Placera   [R] Starta om", True, DARK_GRAY)
        self.screen.blit(hint, (SCREEN_W - hint.get_width() - 6, ui_y+112))

    def draw_level_complete(self):
        """Skärm när en nivå är klar – visar nästa nivå eller vinst."""
        overlay = pygame.Surface((SCREEN_W, ROWS * GRID_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))
        if self.level >= max(LEVEL_WAVES.keys()):
            # Spelat igenom båda nivåerna
            title = self.font_big.render("SPELET KLARAT! ☠  LKAB SÄKRAD!", True, YELLOW)
            sub   = self.font_med.render(f"Slutpoäng: {self.score}  –  Tryck R för att börja om", True, WHITE)
        else:
            title = self.font_big.render(f"NIVÅ {self.level} KLAR!", True, TEAL)
            refund = sum(int(TOWER_TYPES[t.ttype]["cost"]*0.7) for t in self.towers)
            sub   = self.font_med.render(
                f"Torn återbetalas ({refund} kr)  –  Tryck ENTER för Nivå {self.level+1}", True, WHITE)
        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, ROWS*GRID_SIZE//2 - 40))
        self.screen.blit(sub,   (SCREEN_W//2 - sub.get_width()//2,   ROWS*GRID_SIZE//2 + 5))

    def draw_level_transition(self):
        """Kort skärm som presenterar den nya nivån."""
        self.screen.fill(ROCK_BG)
        title = self.font_big.render(f"NIVÅ {self.level}  –  {LEVEL_NAMES[self.level]}", True, TEAL)
        sub   = self.font_med.render("Ny bana, nya fiender – tornplacering börjar om", True, GRAY)
        hint  = self.font_med.render("Tryck ENTER eller MELLANSLAG för att fortsätta", True, WHITE)
        cy2   = SCREEN_H // 2
        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, cy2 - 50))
        self.screen.blit(sub,   (SCREEN_W//2 - sub.get_width()//2,   cy2))
        self.screen.blit(hint,  (SCREEN_W//2 - hint.get_width()//2,  cy2 + 50))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_W, ROWS * GRID_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))
        t = self.font_big.render("GRUVAN FÖRLORAD", True, RED)
        s = self.font_med.render(f"Poäng: {self.score}  –  Tryck R för att starta om", True, WHITE)
        self.screen.blit(t, (SCREEN_W//2 - t.get_width()//2, ROWS*GRID_SIZE//2 - 30))
        self.screen.blit(s, (SCREEN_W//2 - s.get_width()//2, ROWS*GRID_SIZE//2 + 10))

    def get_tower_btn_rect(self, idx):
        btn_w  = 88
        btn_x0 = SCREEN_W - len(TOWER_TYPES) * btn_w - 4
        return pygame.Rect(btn_x0 + idx * btn_w, ROWS * GRID_SIZE + 4, btn_w, 58)

    def run(self):
        tower_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]
        tower_list = list(TOWER_TYPES.keys())
        running = True
        while running:
            self.clock.tick(60)
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.full_reset()

                    # Nivå klar → nästa nivå
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.level_complete and self.level < max(LEVEL_WAVES.keys()):
                            self.begin_next_level()
                        elif self.level_transition:
                            self.level_transition = False

                    # Välj torn med [1-6]
                    for i, k in enumerate(tower_keys):
                        if event.key == k and i < len(tower_list):
                            if self.tower_unlocked(tower_list[i]):
                                self.selected_tower_type = tower_list[i]

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.level_transition:
                        self.level_transition = False
                        continue
                    handled = False
                    for i in range(len(TOWER_TYPES)):
                        if self.get_tower_btn_rect(i).collidepoint(mx, my):
                            ttype = tower_list[i]
                            if self.tower_unlocked(ttype):
                                self.selected_tower_type = ttype
                            handled = True
                            break
                    if not handled:
                        ui_y = ROWS * GRID_SIZE
                        wave_btn = pygame.Rect(8, ui_y+72, 210, 34)
                        if (wave_btn.collidepoint(mx, my) and self.between_waves
                                and self.wave_complete_timer == 0 and not self.level_complete):
                            self.start_wave()
                        elif my < ROWS * GRID_SIZE and not self.level_complete:
                            col, row = px_to_grid(mx, my)
                            clicked = next((t for t in self.towers if t.col==col and t.row==row), None)
                            if clicked:
                                self.selected_tower = clicked if self.selected_tower != clicked else None
                            else:
                                self.selected_tower = None
                                if not self.game_over:
                                    self.place_tower(col, row)

            self.update()

            # --- Rita ---
            if self.level_transition:
                self.draw_level_transition()
            else:
                self.draw_map()

                # Räckviddsförhandsvisning
                if my < ROWS * GRID_SIZE and not self.level_complete:
                    col, row = px_to_grid(mx, my)
                    if not self.grid_occupied(col, row):
                        px3, py3 = grid_to_px(col, row)
                        tdata    = TOWER_TYPES[self.selected_tower_type]
                        unlocked = self.tower_unlocked(self.selected_tower_type)
                        pygame.draw.circle(self.screen,
                                           (200,200,200) if unlocked else DARK_GRAY,
                                           (px3, py3), tdata["range"], 1)
                        hint_col = tdata["color"] if (self.money >= tdata["cost"] and unlocked) else DARK_GRAY
                        pygame.draw.rect(self.screen, hint_col,
                                         (col*GRID_SIZE+3, row*GRID_SIZE+3, GRID_SIZE-6, GRID_SIZE-6), 2)

                for t in self.towers:
                    t.draw(self.screen, selected=(self.selected_tower == t))
                for e in self.effects:
                    e.draw(self.screen)
                for b in self.bullets:
                    b.draw(self.screen)
                for z in self.zombies:
                    z.draw(self.screen)

                self.draw_boss_bar()
                self.draw_ui()
                for banner in self.banners:
                    banner.draw(self.screen, self.font_big)
                self.banners = [b for b in self.banners if b.timer > 0]

                if self.game_over:
                    self.draw_game_over()
                elif self.level_complete:
                    self.draw_level_complete()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
