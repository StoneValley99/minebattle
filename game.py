import pygame
import math
import random

pygame.init()

SCREEN_W, SCREEN_H = 1024, 768
GRID_SIZE = 48
COLS = SCREEN_W // GRID_SIZE   # 21
ROWS = (SCREEN_H - 144) // GRID_SIZE  # 13

# --- Gruvfärger ---
ROCK_BG       = (28, 24, 22)
ROCK_WALL     = (45, 38, 32)
ROCK_LINE     = (38, 32, 28)
ORE_COLOR     = (140, 60, 30)
ORE_VEIN      = (180, 90, 40)
TUNNEL_FLOOR  = (75, 65, 55)
TUNNEL_EDGE   = (55, 48, 40)
UI_BG         = (18, 15, 12)
UI_LINE       = (80, 65, 50)
WHITE         = (255, 255, 255)
BLACK         = (0, 0, 0)
RED           = (220, 50, 50)
YELLOW        = (255, 210, 30)
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
PURPLE        = (160, 40, 200)
DARK_PURPLE   = (60, 10, 80)

WAYPOINTS = [
    (0, 2), (4, 2), (4, 6), (8, 6), (8, 2), (12, 2),
    (12, 10), (16, 10), (16, 6), (20, 6), (20, 12)
]

# unlock_wave: vilket vågantal som krävs för att låsa upp tornet
TOWER_TYPES = {
    "borrhammare": {
        "name": "Borrhammare", "cost": 75,  "unlock_wave": 0,
        "color": (200, 170, 50),  "range": 110,
        "damage": 12, "fire_rate": 20,
        "bullet_color": (220, 200, 80), "bullet_speed": 7,
        "splash": 0, "slow": 0,
        "desc": "Snabb borrning, kort räckvidd",
    },
    "skrotare": {
        "name": "Skrotare",    "cost": 125, "unlock_wave": 0,
        "color": (80, 130, 200), "range": 130,
        "damage": 20, "fire_rate": 40,
        "bullet_color": (120, 180, 255), "bullet_speed": 5,
        "splash": 0, "slow": 70,
        "desc": "Saktar ner, medellång räckvidd",
    },
    "lhd": {
        "name": "LHD",         "cost": 200, "unlock_wave": 3,
        "color": ORANGE,        "range": 105,
        "damage": 45, "fire_rate": 65,
        "bullet_color": (255, 160, 40), "bullet_speed": 5,
        "splash": 45, "slow": 0,
        "desc": "Skopsprängning, träffar flera",
    },
    "sprang": {
        "name": "Sprängare",   "cost": 175, "unlock_wave": 3,
        "color": (210, 40, 40), "range": 140,
        "damage": 80, "fire_rate": 110,
        "bullet_color": (255, 80, 40), "bullet_speed": 4,
        "splash": 60, "slow": 0,
        "desc": "Stor explosion, lång räckvidd",
    },
    "malmkross": {
        "name": "Malmkross",   "cost": 325, "unlock_wave": 5,
        "color": (120, 100, 75), "range": 95,
        "damage": 70, "fire_rate": 50,
        "bullet_color": (180, 150, 100), "bullet_speed": 4,
        "splash": 35, "slow": 50,
        "desc": "Krossar + saktar, kort räckvidd",
    },
    "detonator": {
        "name": "Detonator",   "cost": 475, "unlock_wave": 7,
        "color": (200, 20, 20), "range": 165,
        "damage": 180, "fire_rate": 150,
        "bullet_color": (255, 80, 20), "bullet_speed": 3,
        "splash": 95, "slow": 0,
        "desc": "Massiv explosion, lång räckvidd",
    },
}

ZOMBIE_STATS = {
    "normal":   {"hp": 80,   "speed": 1.2, "reward": 10,  "color": (80,  170, 80),  "size": 10},
    "fast":     {"hp": 50,   "speed": 2.2, "reward": 15,  "color": (200, 200, 50),  "size": 8},
    "tank":     {"hp": 300,  "speed": 0.7, "reward": 30,  "color": (180, 80,  80),  "size": 14},
    "boss":     {"hp": 800,  "speed": 0.5, "reward": 80,  "color": (200, 50,  200), "size": 20},
    "megaboss": {"hp": 4000, "speed": 0.3, "reward": 500, "color": (130, 0,   160), "size": 30},
}

def _w(vag, count, interval, ztype):
    return [{"type": ztype, "count": count, "interval": interval, "wave_unlock": vag}]

ZOMBIE_WAVES = [
    # Våg 1 – introduktion
    _w(1, 8,  60, "normal"),
    # Våg 2
    _w(2, 12, 50, "normal") + _w(2, 5, 40, "fast"),
    # Våg 3 – LHD/Sprängare låses upp
    _w(3, 10, 45, "normal") + _w(3, 8, 35, "fast") + _w(3, 2, 80, "tank"),
    # Våg 4
    _w(4, 15, 40, "fast")   + _w(4, 5, 70, "tank"),
    # Våg 5 – Malmkross låses upp
    _w(5, 20, 40, "normal") + _w(5, 10, 32, "fast") + _w(5, 8, 65, "tank"),
    # Våg 6
    _w(6, 25, 35, "normal") + _w(6, 12, 28, "fast") + _w(6, 10, 55, "tank") + _w(6, 3, 90, "boss"),
    # Våg 7 – Detonator låses upp
    _w(7, 15, 30, "fast")   + _w(7, 12, 50, "tank") + _w(7, 5, 80, "boss"),
    # Våg 8
    _w(8, 30, 28, "normal") + _w(8, 18, 25, "fast") + _w(8, 14, 45, "tank") + _w(8, 6, 70, "boss"),
    # Våg 9
    _w(9, 20, 25, "fast")   + _w(9, 18, 40, "tank") + _w(9, 10, 60, "boss"),
    # Våg 10 – MEGABOSS
    _w(10, 15, 28, "fast")  + _w(10, 10, 45, "tank") + _w(10, 6, 60, "boss") + _w(10, 1, 1, "megaboss"),
]

UNLOCK_MESSAGES = {
    3: "LHD och Sprängare upplåsta!",
    5: "Malmkross upplåst!",
    7: "Detonator upplåst!",
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
    surf = pygame.Surface((SCREEN_W, ROWS * GRID_SIZE))
    surf.fill(ROCK_BG)
    for c in range(COLS):
        for r in range(ROWS):
            x, y = c * GRID_SIZE, r * GRID_SIZE
            if (c, r) not in PATH_CELLS:
                shade = rng.randint(-10, 10)
                col = tuple(max(0, min(255, v + shade)) for v in ROCK_WALL)
                pygame.draw.rect(surf, col, (x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2))
    for _ in range(28):
        cx = rng.randint(0, SCREEN_W)
        cy = rng.randint(0, ROWS * GRID_SIZE)
        gc, gr = px_to_grid(cx, cy)
        if (gc, gr) in PATH_CELLS:
            continue
        length = rng.randint(20, 80)
        angle  = rng.uniform(0, math.pi * 2)
        ex = int(cx + math.cos(angle) * length)
        ey = int(cy + math.sin(angle) * length)
        pygame.draw.line(surf, ORE_VEIN, (cx, cy), (ex, ey), rng.randint(1, 3))
        for _ in range(rng.randint(2, 5)):
            bx = cx + rng.randint(-12, 12)
            by = cy + rng.randint(-12, 12)
            pygame.draw.circle(surf, ORE_COLOR, (bx, by), rng.randint(2, 5))
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
    for c, r in PATH_CELLS:
        x, y = c * GRID_SIZE, r * GRID_SIZE
        pygame.draw.rect(surf, TUNNEL_FLOOR, (x, y, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surf, TUNNEL_EDGE,  (x, y, GRID_SIZE, GRID_SIZE), 1)
        for _ in range(4):
            gx = x + rng.randint(4, GRID_SIZE - 4)
            gy = y + rng.randint(4, GRID_SIZE - 4)
            pygame.draw.circle(surf, TUNNEL_EDGE, (gx, gy), 1)
    for c in range(COLS + 1):
        pygame.draw.line(surf, ROCK_LINE, (c * GRID_SIZE, 0), (c * GRID_SIZE, ROWS * GRID_SIZE), 1)
    for r in range(ROWS + 1):
        pygame.draw.line(surf, ROCK_LINE, (0, r * GRID_SIZE), (SCREEN_W, r * GRID_SIZE), 1)
    for wp in [WAYPOINTS[0], WAYPOINTS[-1]]:
        wx, wy = wp[0] * GRID_SIZE, wp[1] * GRID_SIZE
        for i in range(4):
            stripe_col = WARN_YELLOW if i % 2 == 0 else WARN_BLACK
            pygame.draw.rect(surf, stripe_col, (wx + i * (GRID_SIZE // 4), wy, GRID_SIZE // 4, GRID_SIZE))
    return surf


class Zombie:
    def __init__(self, ztype):
        stats = ZOMBIE_STATS[ztype]
        self.ztype     = ztype
        self.max_hp    = stats["hp"]
        self.hp        = self.max_hp
        self.base_speed = stats["speed"]
        self.speed     = self.base_speed
        self.reward    = stats["reward"]
        self.color     = stats["color"]
        self.size      = stats["size"]
        self.waypoint_idx = 0
        px, py = grid_to_px(*WAYPOINTS[0])
        self.x = float(px)
        self.y = float(py)
        self.alive       = True
        self.reached_end = False
        self.slow_timer  = 0
        self.progress    = 0.0

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
        if self.ztype == "megaboss":
            self._draw_megaboss(surface, cx, cy)
            return
        pygame.draw.circle(surface, (0, 0, 0), (cx + 2, cy + 2), self.size)
        pygame.draw.circle(surface, self.color, (cx, cy), self.size)
        helmet_col = (220, 180, 30) if self.ztype != "boss" else (200, 30, 200)
        pygame.draw.arc(surface, helmet_col,
                        (cx - self.size, cy - self.size - 2, self.size * 2, self.size + 2),
                        0, math.pi, 3)
        pygame.draw.circle(surface, YELLOW, (cx, cy - self.size + 1), 2)
        eye_off = max(2, self.size // 3)
        pygame.draw.circle(surface, WHITE, (cx - eye_off, cy - 2), 3)
        pygame.draw.circle(surface, WHITE, (cx + eye_off, cy - 2), 3)
        pygame.draw.circle(surface, BLACK, (cx - eye_off + 1, cy - 2), 1)
        pygame.draw.circle(surface, BLACK, (cx + eye_off + 1, cy - 2), 1)
        bar_w = self.size * 2
        bar_x = cx - self.size
        bar_y = cy - self.size - 10
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_w, 4))
        pygame.draw.rect(surface, GREEN,     (bar_x, bar_y, int(bar_w * self.hp / self.max_hp), 4))
        if self.slow_timer > 0:
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), self.size + 3, 2)

    def _draw_megaboss(self, surface, cx, cy):
        s = self.size
        # Pulsande glöd
        glow_r = s + 8 + int(4 * math.sin(pygame.time.get_ticks() * 0.005))
        pygame.draw.circle(surface, (60, 0, 80), (cx, cy), glow_r)
        # Kropp
        pygame.draw.circle(surface, (0, 0, 0),   (cx + 3, cy + 3), s)
        pygame.draw.circle(surface, self.color,   (cx, cy), s)
        # Yttre ring
        pygame.draw.circle(surface, (200, 100, 255), (cx, cy), s, 3)
        # Stor hotfull hjälm
        pygame.draw.arc(surface, (180, 0, 180),
                        (cx - s, cy - s - 4, s * 2, s + 4), 0, math.pi, 5)
        # Pannlampa (stor)
        pygame.draw.circle(surface, (255, 255, 100), (cx, cy - s + 2), 5)
        pygame.draw.circle(surface, WHITE,           (cx, cy - s + 2), 3)
        # Ögon (röda, stora)
        eye_off = s // 3
        for ex, ey in [(cx - eye_off, cy - 4), (cx + eye_off, cy - 4)]:
            pygame.draw.circle(surface, (255, 50, 50), (ex, ey), 5)
            pygame.draw.circle(surface, (255, 200, 0), (ex, ey), 2)
        # Mun (tandad)
        for i in range(-s // 2, s // 2, 6):
            pygame.draw.line(surface, (255, 50, 50),
                             (cx + i, cy + s // 2), (cx + i + 3, cy + s // 2 + 5), 2)
        # HP-bar (bred)
        bar_w = s * 3
        bar_x = cx - s - s // 2
        bar_y = cy - s - 14
        pygame.draw.rect(surface, (80, 0, 0),  (bar_x, bar_y, bar_w, 6))
        pygame.draw.rect(surface, PURPLE,      (bar_x, bar_y, int(bar_w * self.hp / self.max_hp), 6))
        pygame.draw.rect(surface, WHITE,       (bar_x, bar_y, bar_w, 6), 1)


class Bullet:
    def __init__(self, x, y, target, speed, damage, color, splash, slow):
        self.x, self.y = float(x), float(y)
        self.target    = target
        self.speed     = speed
        self.damage    = damage
        self.color     = color
        self.splash    = splash
        self.slow      = slow
        self.alive     = True

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
        pygame.draw.circle(surface, WHITE,      (int(self.x), int(self.y)), 2)


class Tower:
    def __init__(self, col, row, ttype):
        self.col, self.row = col, row
        self.ttype = ttype
        data = TOWER_TYPES[ttype]
        self.color        = data["color"]
        self.range        = data["range"]
        self.damage       = data["damage"]
        self.fire_rate    = data["fire_rate"]
        self.bullet_color = data["bullet_color"]
        self.bullet_speed = data["bullet_speed"]
        self.splash       = data["splash"]
        self.slow         = data["slow"]
        self.cooldown     = 0
        self.x, self.y    = grid_to_px(col, row)
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
        draw = {
            "borrhammare": self._draw_borrhammare,
            "skrotare":    self._draw_skrotare,
            "lhd":         self._draw_lhd,
            "sprang":      self._draw_sprang,
            "malmkross":   self._draw_malmkross,
            "detonator":   self._draw_detonator,
        }
        draw[self.ttype](surface, cx, cy, hs)
        if selected:
            pygame.draw.circle(surface, WHITE, (cx, cy), self.range, 1)

    def _draw_borrhammare(self, surface, cx, cy, hs):
        pygame.draw.rect(surface, WARN_BLACK,  (cx - hs,     cy - hs,      hs * 2,     hs * 2))
        pygame.draw.rect(surface, WARN_YELLOW, (cx - hs + 2, cy - hs + 2,  hs * 2 - 4, hs * 2 - 4))
        bx = cx + int(math.cos(self.angle) * (hs + 10))
        by = cy + int(math.sin(self.angle) * (hs + 10))
        pygame.draw.line(surface, STEEL, (cx, cy), (bx, by), 5)
        pygame.draw.circle(surface, DARK_GRAY, (bx, by), 4)
        pygame.draw.circle(surface, LKAB_BLUE, (cx, cy), 4)

    def _draw_skrotare(self, surface, cx, cy, hs):
        pygame.draw.rect(surface, DARK_GRAY,    (cx - hs,     cy - hs,     hs * 2,     hs * 2))
        pygame.draw.rect(surface, (80, 130, 200), (cx - hs + 2, cy - hs + 2, hs * 2 - 4, hs * 2 - 4))
        ax = cx + int(math.cos(self.angle) * hs)
        ay = cy + int(math.sin(self.angle) * hs)
        pygame.draw.line(surface, STEEL, (cx, cy), (ax, ay), 6)
        ex = cx + int(math.cos(self.angle) * (hs + 8))
        ey = cy + int(math.sin(self.angle) * (hs + 8))
        pygame.draw.circle(surface, GRAY, (ex, ey), 5)
        pygame.draw.circle(surface, WHITE, (cx, cy), 3)

    def _draw_lhd(self, surface, cx, cy, hs):
        pygame.draw.rect(surface, WARN_BLACK, (cx - hs,     cy - hs + 4, hs * 2,     hs * 2 - 8))
        pygame.draw.rect(surface, ORANGE,    (cx - hs + 2, cy - hs + 6, hs * 2 - 4, hs * 2 - 12))
        for dx, dy in [(-hs + 4, hs - 4), (hs - 4, hs - 4), (-hs + 4, -hs + 4), (hs - 4, -hs + 4)]:
            pygame.draw.circle(surface, DARK_GRAY, (cx + dx, cy + dy), 4)
            pygame.draw.circle(surface, GRAY,      (cx + dx, cy + dy), 2)
        sx = cx + int(math.cos(self.angle) * (hs + 4))
        sy = cy + int(math.sin(self.angle) * (hs + 4))
        pygame.draw.line(surface, STEEL, (cx, cy), (sx, sy), 7)

    def _draw_sprang(self, surface, cx, cy, hs):
        for i in range(4):
            stripe = WARN_YELLOW if i % 2 == 0 else RED
            pygame.draw.rect(surface, stripe, (cx - hs + i * (hs // 2), cy - hs, hs // 2, hs * 2))
        pygame.draw.ellipse(surface, (180, 30, 30), (cx - hs // 2, cy - hs + 4, hs, hs * 2 - 8))
        fuse_x = cx + int(math.cos(self.angle) * (hs + 6))
        fuse_y = cy + int(math.sin(self.angle) * (hs + 6))
        pygame.draw.line(surface, WARN_YELLOW, (cx, cy), (fuse_x, fuse_y), 2)
        pygame.draw.circle(surface, YELLOW, (fuse_x, fuse_y), 3)

    def _draw_malmkross(self, surface, cx, cy, hs):
        # Tung grå krossmaskin
        pygame.draw.rect(surface, (60, 50, 40),   (cx - hs,     cy - hs,     hs * 2,     hs * 2))
        pygame.draw.rect(surface, (120, 100, 75),  (cx - hs + 2, cy - hs + 2, hs * 2 - 4, hs * 2 - 4))
        # Krossarm
        ax = cx + int(math.cos(self.angle) * (hs + 6))
        ay = cy + int(math.sin(self.angle) * (hs + 6))
        pygame.draw.line(surface, (80, 65, 50), (cx, cy), (ax, ay), 8)
        # Krossblock vid spetsen
        pygame.draw.rect(surface, (90, 75, 60),
                         (ax - 6, ay - 6, 12, 12))
        pygame.draw.rect(surface, WARN_YELLOW,
                         (ax - 6, ay - 6, 12, 12), 1)
        pygame.draw.circle(surface, (160, 130, 90), (cx, cy), 4)

    def _draw_detonator(self, surface, cx, cy, hs):
        # Röd detonationsstation
        pygame.draw.rect(surface, (80, 0, 0),    (cx - hs,     cy - hs,     hs * 2,     hs * 2))
        pygame.draw.rect(surface, (200, 20, 20),  (cx - hs + 2, cy - hs + 2, hs * 2 - 4, hs * 2 - 4))
        # Tre detonatorknappar
        for i, bx in enumerate([cx - 8, cx, cx + 8]):
            col = WARN_YELLOW if (pygame.time.get_ticks() // 200 + i) % 3 == 0 else (160, 160, 0)
            pygame.draw.circle(surface, col, (bx, cy + 4), 4)
        # Ledning mot mål
        ex = cx + int(math.cos(self.angle) * (hs + 8))
        ey = cy + int(math.sin(self.angle) * (hs + 8))
        pygame.draw.line(surface, WARN_YELLOW, (cx, cy - 4), (ex, ey), 2)
        pygame.draw.circle(surface, (255, 120, 50), (ex, ey), 4)


class SplashEffect:
    def __init__(self, x, y, radius, big=False):
        self.x, self.y  = x, y
        self.radius     = radius
        self.timer      = 30 if big else 20
        self.max_timer  = self.timer
        self.big        = big

    def update(self):
        self.timer -= 1

    def draw(self, surface):
        frac = self.timer / self.max_timer
        r = int(self.radius * (1 - frac) + 6)
        if self.big:
            col = (255, int(160 * frac), 0)
            pygame.draw.circle(surface, col,    (int(self.x), int(self.y)), r,     4)
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), max(1, r - 6), 2)
        else:
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), r, 2)


class UnlockBanner:
    def __init__(self, text):
        self.text  = text
        self.timer = 180

    def draw(self, surface, font):
        if self.timer <= 0:
            return
        alpha = min(255, self.timer * 3)
        t = font.render(f"★  {self.text}  ★", True, WARN_YELLOW)
        x = SCREEN_W // 2 - t.get_width() // 2
        y = ROWS * GRID_SIZE // 2 - 20
        bg = pygame.Surface((t.get_width() + 20, t.get_height() + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, min(180, alpha)))
        surface.blit(bg, (x - 10, y - 5))
        surface.blit(t, (x, y))
        self.timer -= 1


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("MineBattle – LKAB Gruvförsvar")
        self.clock      = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 17)
        self.font_small = pygame.font.SysFont("Arial", 12)
        self.rng        = random.Random(42)
        self.bg_surface = make_mine_background(self.rng)
        self.reset()

    def reset(self):
        self.towers       = []
        self.zombies      = []
        self.bullets      = []
        self.effects      = []
        self.banners      = []
        self.money        = 200
        self.lives        = 20
        self.score        = 0
        self.wave         = 0
        self.wave_active  = False
        self.spawn_queue  = []
        self.spawn_timer  = 0
        self.selected_tower_type  = "borrhammare"
        self.selected_tower       = None
        self.game_over    = False
        self.victory      = False
        self.between_waves       = True
        self.wave_complete_timer = 0
        self.all_waves_done      = False

    def tower_unlocked(self, ttype):
        return self.wave >= TOWER_TYPES[ttype]["unlock_wave"]

    def start_wave(self):
        if self.wave >= len(ZOMBIE_WAVES):
            self.all_waves_done = True
            return
        self.wave_active  = True
        self.between_waves = False
        self.spawn_queue  = []
        for group in ZOMBIE_WAVES[self.wave]:
            for _ in range(group["count"]):
                self.spawn_queue.append((group["type"], group["interval"]))
        self.spawn_timer = 0
        self.wave += 1
        if self.wave in UNLOCK_MESSAGES:
            self.banners.append(UnlockBanner(UNLOCK_MESSAGES[self.wave]))

    def handle_spawn(self):
        if not self.wave_active or not self.spawn_queue:
            if self.wave_active and not self.spawn_queue and not self.zombies:
                self.wave_active   = False
                self.between_waves = True
                self.wave_complete_timer = 120
                self.money += 50 + self.wave * 10
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
        if not self.tower_unlocked(self.selected_tower_type):
            return
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
        if self.all_waves_done and not self.zombies and not self.wave_active:
            self.victory = True

    # ------------------------------------------------------------------ draw

    def draw_map(self):
        self.screen.blit(self.bg_surface, (0, 0))
        for c, r in PATH_CELLS:
            x, y = c * GRID_SIZE, r * GRID_SIZE
            for nc, nr, side in [(c-1,r,'L'),(c+1,r,'R'),(c,r-1,'T'),(c,r+1,'B')]:
                if (nc, nr) not in PATH_CELLS:
                    wall = (100, 88, 70)
                    if side == 'L':
                        pygame.draw.line(self.screen, wall, (x, y), (x, y + GRID_SIZE), 2)
                    elif side == 'R':
                        pygame.draw.line(self.screen, wall, (x + GRID_SIZE, y), (x + GRID_SIZE, y + GRID_SIZE), 2)
                    elif side == 'T':
                        pygame.draw.line(self.screen, wall, (x, y), (x + GRID_SIZE, y), 2)
                    elif side == 'B':
                        pygame.draw.line(self.screen, wall, (x, y + GRID_SIZE), (x + GRID_SIZE, y + GRID_SIZE), 2)
        sx, sy = grid_to_px(*WAYPOINTS[0])
        ex, ey = grid_to_px(*WAYPOINTS[-1])
        s = self.font_small.render("INGÅNG", True, BLACK)
        e = self.font_small.render("UTGÅNG", True, BLACK)
        self.screen.blit(s, (sx - s.get_width() // 2, sy - 7))
        self.screen.blit(e, (ex - e.get_width() // 2, ey - 7))

    def draw_boss_bar(self):
        mb = next((z for z in self.zombies if z.ztype == "megaboss"), None)
        if not mb:
            return
        bar_w = 500
        bar_x = SCREEN_W // 2 - bar_w // 2
        bar_y = 6
        pygame.draw.rect(self.screen, (40, 0, 50),  (bar_x - 2, bar_y - 2, bar_w + 4, 18))
        pygame.draw.rect(self.screen, (80, 0, 0),   (bar_x, bar_y, bar_w, 14))
        fill = int(bar_w * mb.hp / mb.max_hp)
        pygame.draw.rect(self.screen, PURPLE,       (bar_x, bar_y, fill, 14))
        pygame.draw.rect(self.screen, WHITE,        (bar_x, bar_y, bar_w, 14), 1)
        label = self.font_small.render(f"☠  MEGA-BOSS  {mb.hp}/{mb.max_hp}", True, WHITE)
        self.screen.blit(label, (SCREEN_W // 2 - label.get_width() // 2, bar_y))

    def draw_ui(self):
        ui_y = ROWS * GRID_SIZE
        pygame.draw.rect(self.screen, UI_BG,  (0, ui_y, SCREEN_W, SCREEN_H - ui_y))
        pygame.draw.line(self.screen, UI_LINE, (0, ui_y), (SCREEN_W, ui_y), 2)

        # --- Stats (kompakt, vänster) ---
        stats = [
            (f"Liv: {self.lives}", RED),
            (f"{self.money} kr",   YELLOW),
            (f"Våg: {self.wave}/{len(ZOMBIE_WAVES)}", WHITE),
            (f"Poäng: {self.score}", LIGHT_YELLOW),
        ]
        sx = 8
        for text, col in stats:
            surf = self.font_big.render(text, True, col)
            self.screen.blit(surf, (sx, ui_y + 6))
            sx += surf.get_width() + 18

        # --- Tornknappar (höger, 6 stycken) ---
        btn_w  = 88
        btn_h  = 58
        btn_x0 = SCREEN_W - len(TOWER_TYPES) * btn_w - 4
        for i, (ttype, data) in enumerate(TOWER_TYPES.items()):
            bx        = btn_x0 + i * btn_w
            by        = ui_y + 4
            unlocked  = self.tower_unlocked(ttype)
            affordable = self.money >= data["cost"] and unlocked
            selected  = self.selected_tower_type == ttype

            bg_col  = (40, 34, 28) if unlocked else (22, 18, 16)
            bdr_col = WARN_YELLOW if selected else (UI_LINE if unlocked else DARK_GRAY)

            pygame.draw.rect(self.screen, bg_col,  (bx,     by,     btn_w,     btn_h))
            pygame.draw.rect(self.screen, bdr_col, (bx,     by,     btn_w,     btn_h), 2)

            if unlocked:
                # Färgchip
                pygame.draw.rect(self.screen, data["color"], (bx + 4, by + 5, 10, 10))
                name = self.font_small.render(data["name"], True, WHITE if affordable else GRAY)
                cost = self.font_small.render(f"{data['cost']} kr", True, YELLOW if affordable else RED)
                key  = self.font_small.render(f"[{i+1}]", True, GRAY)
                self.screen.blit(name, (bx + 16, by + 5))
                self.screen.blit(cost, (bx + 16, by + 22))
                self.screen.blit(key,  (bx + 16, by + 39))
            else:
                lock = self.font_small.render(data["name"], True, DARK_GRAY)
                info = self.font_small.render(f"Lås upp V{data['unlock_wave']}", True, (100, 80, 60))
                self.screen.blit(lock, (bx + 4, by + 8))
                self.screen.blit(info, (bx + 4, by + 26))

        # --- Vågknapp (vänster, under stats) ---
        if self.between_waves and not self.all_waves_done:
            if self.wave_complete_timer > 0:
                bonus = 50 + self.wave * 10
                label = f"+{bonus} kr! Nästa våg snart..."
                btn_col = (20, 60, 20)
            elif self.wave < len(ZOMBIE_WAVES):
                label = f"► Starta Våg {self.wave + 1}"
                btn_col = (20, 80, 20)
            else:
                label = "► SLUTVÅG!"
                btn_col = (80, 20, 20)
            btn = pygame.Rect(8, ui_y + 72, 200, 34)
            pygame.draw.rect(self.screen, btn_col, btn)
            pygame.draw.rect(self.screen, GREEN if "Starta" in label else RED, btn, 2)
            t = self.font_med.render(label, True, WHITE)
            self.screen.blit(t, (btn.x + btn.w // 2 - t.get_width() // 2, btn.y + 8))

        # --- Info / kontroller ---
        if self.selected_tower:
            t  = self.selected_tower
            d  = TOWER_TYPES[t.ttype]
            info = f"{d['name']}  |  Räckvidd: {t.range}  |  Skada: {t.damage}  |  {d['desc']}"
            self.screen.blit(self.font_small.render(info, True, LIGHT_YELLOW), (215, ui_y + 78))
        else:
            d = TOWER_TYPES[self.selected_tower_type]
            info = f"Valt: {d['name']}  –  {d['desc']}"
            self.screen.blit(self.font_small.render(info, True, GRAY), (215, ui_y + 78))

        hint = self.font_small.render("[1-6] Välj maskin   [Klicka] Placera   [R] Starta om", True, DARK_GRAY)
        self.screen.blit(hint, (SCREEN_W - hint.get_width() - 6, ui_y + 112))

    def draw_overlay(self):
        if self.game_over:
            self._draw_message("GRUVAN FÖRLORAD",
                               f"Poäng: {self.score}  –  Tryck R för att starta om", RED)
        elif self.victory:
            self._draw_message("GRUVAN SÄKRAD!",
                               f"Alla 10 vågor klarade! Poäng: {self.score}  –  Tryck R", YELLOW)

    def _draw_message(self, title, sub, color):
        overlay = pygame.Surface((SCREEN_W, ROWS * GRID_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))
        t = self.font_big.render(title, True, color)
        s = self.font_med.render(sub,   True, WHITE)
        self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, ROWS * GRID_SIZE // 2 - 30))
        self.screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, ROWS * GRID_SIZE // 2 + 10))

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
                        self.reset()
                    for i, k in enumerate(tower_keys):
                        if event.key == k and i < len(tower_list):
                            if self.tower_unlocked(tower_list[i]):
                                self.selected_tower_type = tower_list[i]
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
                        wave_btn = pygame.Rect(8, ui_y + 72, 200, 34)
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

            # Räckviddsförhandsvisning
            if my < ROWS * GRID_SIZE:
                col, row = px_to_grid(mx, my)
                if not self.grid_occupied(col, row):
                    px2, py2 = grid_to_px(col, row)
                    tdata = TOWER_TYPES[self.selected_tower_type]
                    unlocked = self.tower_unlocked(self.selected_tower_type)
                    pygame.draw.circle(self.screen, (200, 200, 200) if unlocked else DARK_GRAY,
                                       (px2, py2), tdata["range"], 1)
                    hint_col = tdata["color"] if (self.money >= tdata["cost"] and unlocked) else DARK_GRAY
                    pygame.draw.rect(self.screen, hint_col,
                                     (col * GRID_SIZE + 3, row * GRID_SIZE + 3, GRID_SIZE - 6, GRID_SIZE - 6), 2)

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
            self.draw_overlay()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
