import asyncio
import array
import pygame
import math
import random
import sys
import os

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
MONEY_LOSS_FONT = pygame.font.SysFont("Arial", 18, bold=True)
PART_FONT       = pygame.font.SysFont("Arial", 11, bold=True)

def make_placement_sound():
    try:
        sample_rate = 44100
        duration = 0.26
        total_samples = int(sample_rate * duration)
        samples = array.array('h')
        for i in range(total_samples):
            t = i / sample_rate
            if t < 0.12:
                # rising "wzzzp" tone
                freq = 400 + 900 * (t / 0.12)
                envelope = 0.9 * (1 - (t / 0.12))
                sample = math.sin(2 * math.pi * freq * t) * 22000 * envelope
            else:
                # boom noise and low thud
                u = (t - 0.12) / (duration - 0.12)
                envelope = max(0, 0.8 * (1 - u))
                noise = math.sin(2 * math.pi * 160 * t) * 0.5 + math.sin(2 * math.pi * 80 * t) * 0.5
                sample = noise * 18000 * envelope
            samples.append(max(-32768, min(32767, int(sample))))
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except Exception:
        return None

SCREEN_W, SCREEN_H = 1024, 768
GRID_SIZE = 48
COLS = SCREEN_W // GRID_SIZE   # 21
ROWS = (SCREEN_H - 144) // GRID_SIZE  # 13
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(ROOT_DIR, "media")
MUSIC_FILE = os.path.join(MEDIA_DIR, "idoberg-relaxing-guitar-loop-v5-245859.mp3")
INTRO_FILE = os.path.join(MEDIA_DIR, "9jackjack8-signal-dark-rock-hip-hop-intro-411337.mp3")
HORN_FILE = os.path.join(MEDIA_DIR, "submority-traimory-mega-horn-angry-siren-f-cinematic-trailer-sound-effects-193408.mp3")
CYBER_FILE = os.path.join(MEDIA_DIR, "vasilyatsevich-brain-implant-cyberpunk-sci-fi-trailer-action-intro-330416.mp3")
CLICK_SOUND_FILE = os.path.join(MEDIA_DIR, "koiroylers-gear-click-351962.mp3")
STAMP_SOUND_FILE = os.path.join(MEDIA_DIR, "freesound_community-stamp-81635.mp3")
BOOM_SOUND_FILE = os.path.join(MEDIA_DIR, "universfield-impact-cinematic-boom-352465.mp3")

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
PANEL_BG     = (24, 22, 20)
PANEL_BORDER = (110, 95, 70)
PANEL_HIGHLIGHT = (185, 170, 130)
BADGE_BG     = (38, 33, 30)
BADGE_BORDER = (135, 120, 95)
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

# ── Vapendelar ────────────────────────────────────────────────────────────────
PART_TYPES = {
    "kugge":    {"name": "Kugge",     "color": (200, 195,  55)},
    "laddning": {"name": "Laddning",  "color": (255,  75,  25)},
    "borrspets":{"name": "Borrspets", "color": ( 50, 185, 255)},
}

PART_RECIPES = [
    {"id": "pengar",         "name": "Skrotinsamling",     "desc": "+300 kr direkt",
     "parts": ["kugge", "kugge"],                           "effect": "money",      "amount": 300},
    {"id": "boost",          "name": "Sprängladdat skift", "desc": "x2 skada 1 våg",
     "parts": ["laddning", "laddning"],                     "effect": "damage_boost"},
    {"id": "gratssprang",    "name": "Gratis Sprängare",   "desc": "Placera en Sprängare gratis",
     "parts": ["laddning", "borrspets"],                    "effect": "free_tower",  "tower": "sprang"},
    {"id": "gratslhd",       "name": "Gratis LHD",         "desc": "Placera en LHD gratis",
     "parts": ["kugge", "borrspets"],                       "effect": "free_tower",  "tower": "lhd"},
    {"id": "detonator_free", "name": "Gratis Detonator",   "desc": "Placera en Detonator gratis",
     "parts": ["laddning", "laddning", "borrspets"],        "effect": "free_tower",  "tower": "detonator"},
]

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

def make_mine_background(rng, path_cells, level=1, waypoints=None):
    surf = pygame.Surface((SCREEN_W, SCREEN_H))
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
    if waypoints is None:
        waypoints = [LEVEL_WAYPOINTS[level][0], LEVEL_WAYPOINTS[level][-1]]

    # Varningsränder ingång/utgång
    for wp in [waypoints[0], waypoints[-1]]:
        wx, wy = wp[0] * GRID_SIZE, wp[1] * GRID_SIZE
        for i in range(4):
            stripe_col = WARN_YELLOW if i % 2 == 0 else WARN_BLACK
            pygame.draw.rect(surf, stripe_col, (wx + i * (GRID_SIZE // 4), wy, GRID_SIZE // 4, GRID_SIZE))

    # Start door visuals
    sx, sy = waypoints[0][0] * GRID_SIZE, waypoints[0][1] * GRID_SIZE
    door = pygame.Rect(sx + 8, sy + GRID_SIZE - 32, GRID_SIZE - 16, 28)
    pygame.draw.rect(surf, (80, 55, 35), door, border_radius=8)
    pygame.draw.rect(surf, (180, 160, 120), door.inflate(-8, -8), 3, border_radius=6)
    for i in range(1, 3):
        px = door.x + i * door.w // 3
        pygame.draw.line(surf, (120, 90, 60), (px, door.y + 6), (px, door.y + door.h - 6), 2)
    pygame.draw.circle(surf, (220, 200, 120), (door.centerx, door.y + 8), 5)

    # End post visuals
    ex, ey = waypoints[-1][0] * GRID_SIZE, waypoints[-1][1] * GRID_SIZE
    post_x = ex + GRID_SIZE - 16
    post_y = ey + 8
    pygame.draw.rect(surf, (90, 70, 50), (post_x, post_y, 10, GRID_SIZE - 16), border_radius=3)
    for i in range(3):
        col = WARN_YELLOW if i % 2 == 0 else WARN_BLACK
        pygame.draw.rect(surf, col, (post_x - 18, post_y + i * 12, 18, 10))
    pygame.draw.rect(surf, (220, 230, 255), (post_x - 20, post_y - 18, 28, 14), border_radius=5)
    pygame.draw.polygon(surf, (30, 30, 30), [(post_x - 16, post_y - 14), (post_x - 8, post_y - 22), (post_x - 0, post_y - 14)])

    return surf


def generate_procedural_waypoints(level, rng):
    # Starta och sluta i mitten av kartan vertikalt
    mid_lo = ROWS // 3
    mid_hi = ROWS * 2 // 3
    start_row = rng.randint(mid_lo, mid_hi)
    end_row   = rng.randint(mid_lo, mid_hi)
    segment_count = 5 + min(3, level)
    waypoints = [(0, start_row)]
    last_col = 0
    last_row = start_row
    for segment in range(1, segment_count + 1):
        if segment == segment_count:
            target_col = COLS - 1
            target_row = end_row
        else:
            min_col = last_col + 2
            max_col = max(min_col, int((COLS - 1) * segment / (segment_count + 1)) + 2)
            target_col = rng.randint(min_col, min(COLS - 2, max_col))
            # Tillåt 4 raders rörelse för mer vindlande bana
            target_row = rng.randint(max(1, last_row - 4), min(ROWS - 2, last_row + 4))
        if target_col <= last_col:
            target_col = min(COLS - 2, last_col + 2)
        if target_row != last_row:
            waypoints.append((target_col, last_row))
            waypoints.append((target_col, target_row))
        else:
            waypoints.append((target_col, last_row))
        last_col, last_row = target_col, target_row

    compressed = []
    for wp in waypoints:
        if not compressed or wp != compressed[-1]:
            compressed.append(wp)
    return compressed

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

    def update(self, speed_mul=1.0):
        if self.slow_timer > 0:
            self.slow_timer -= speed_mul
            self.speed = self.base_speed * 0.55 * speed_mul   # mjukare bromsa
        else:
            self.speed = self.base_speed * speed_mul
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

    def draw(self, surface, shake=(0, 0)):
        cx, cy = int(self.x) + shake[0], int(self.y) + shake[1]
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
        # Färg: sjuklig grön (normal), gulblek (fast), mörkröd (tank), lila (boss)
        body_col = self.color
        # Skugga
        pygame.draw.circle(surface, (0, 0, 0), (cx + 2, cy + 2), s)
        # Kropp
        pygame.draw.circle(surface, body_col, (cx, cy), s)
        # Förruttnelsefläckar på kroppen
        spot = tuple(max(0, v - 50) for v in body_col)
        pygame.draw.circle(surface, spot, (cx - s//3, cy + s//4), max(2, s//4))
        pygame.draw.circle(surface, spot, (cx + s//3, cy - s//5), max(1, s//5))
        # Glödande röda ögon
        eye_off = max(2, s // 3)
        for ex2 in [cx - eye_off, cx + eye_off]:
            pygame.draw.circle(surface, (160, 0, 0),   (ex2, cy - s//4), 4)   # röd glöd
            pygame.draw.circle(surface, (255, 60, 0),  (ex2, cy - s//4), 3)   # orange
            pygame.draw.circle(surface, (255, 220, 0), (ex2, cy - s//4), 1)   # gul pupill
        # Tandad mun
        mouth_y = cy + s // 3
        pygame.draw.line(surface, (20, 0, 0), (cx - s//2, mouth_y), (cx + s//2, mouth_y), 1)
        for i in range(4):
            tx = cx - s//2 + 2 + i * (s // 4)
            pygame.draw.polygon(surface, (230, 220, 200),   # tand
                                [(tx, mouth_y), (tx + 3, mouth_y), (tx + 1, mouth_y + 4)])
        # Sår/stygn på boss
        if self.ztype == "boss":
            pygame.draw.line(surface, (180, 0, 0), (cx - 4, cy - s + 4), (cx + 4, cy - s + 4), 2)
            for sx2 in range(cx - 3, cx + 4, 3):
                pygame.draw.line(surface, (180, 0, 0), (sx2, cy - s + 2), (sx2, cy - s + 6), 1)
        self._draw_hp_bar(surface, cx, cy, s)
        if self.slow_timer > 0:
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), s + 3, 2)

    def _draw_rusher(self, surface, cx, cy):
        s = self.size
        # Liten, sjukt gul, snabb zombie – skeletttunn
        pygame.draw.circle(surface, (0, 0, 0), (cx + 1, cy + 1), s)
        pygame.draw.circle(surface, (180, 180, 60), (cx, cy), s)   # gulblek
        # Urgröpta kindben
        pygame.draw.circle(surface, (120, 120, 20), (cx - 3, cy + 1), 2)
        pygame.draw.circle(surface, (120, 120, 20), (cx + 3, cy + 1), 2)
        # Galna stirrande ögon – vita med röd iris
        for ex2 in [cx - 3, cx + 3]:
            pygame.draw.circle(surface, WHITE,        (ex2, cy - 2), 3)
            pygame.draw.circle(surface, (220, 30, 0), (ex2, cy - 2), 2)
            pygame.draw.circle(surface, BLACK,        (ex2, cy - 2), 1)
        # Skrikande mun
        pygame.draw.ellipse(surface, (10, 0, 0), (cx - 3, cy + 2, 6, 4))
        self._draw_hp_bar(surface, cx, cy, s)
        if self.slow_timer > 0:
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), s + 2, 1)

    def _draw_bergtroll(self, surface, cx, cy):
        s = self.size
        # Massiv, klumpig zombie – grå med röta
        pygame.draw.circle(surface, (0, 0, 0), (cx + 3, cy + 3), s)
        pygame.draw.circle(surface, (110, 85, 55), (cx, cy), s)    # murken brun
        # Klumpiga bölder/köttstycken
        for dx2, dy2, r2 in [(-6, -4, 4), (5, -5, 3), (-4, 5, 3), (6, 4, 4)]:
            pygame.draw.circle(surface, (85, 60, 35), (cx + dx2, cy + dy2), r2)
        # Röda hålögon
        eye_off = s // 3
        for ex2 in [cx - eye_off, cx + eye_off]:
            pygame.draw.circle(surface, (40, 0, 0),   (ex2, cy - 3), 5)
            pygame.draw.circle(surface, (200, 20, 0), (ex2, cy - 3), 3)
            pygame.draw.circle(surface, (255, 80, 0), (ex2, cy - 3), 1)
        # Söndersliten mun med huggtänder
        pygame.draw.line(surface, (20, 0, 0), (cx - s//2 + 2, cy + s//3), (cx + s//2 - 2, cy + s//3), 2)
        for tx in [cx - 5, cx, cx + 5]:
            pygame.draw.polygon(surface, (210, 200, 180),
                                [(tx - 2, cy + s//3), (tx + 2, cy + s//3), (tx, cy + s//3 + 5)])
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

    def update(self, zombies, speed_mul=1.0):
        actual_speed = self.speed * speed_mul
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
        if dist < actual_speed + 4:
            self._hit(zombies)
        else:
            self.x += dx / dist * actual_speed
            self.y += dy / dist * actual_speed

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

    def draw(self, surface, shake=(0, 0)):
        pygame.draw.circle(surface, self.color, (int(self.x) + shake[0], int(self.y) + shake[1]), 4)
        pygame.draw.circle(surface, WHITE,      (int(self.x) + shake[0], int(self.y) + shake[1]), 2)


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

    def update(self, zombies, bullets, speed_mul=1.0, damage_mul=1.0):
        if self.cooldown > 0:
            self.cooldown -= speed_mul
            return
        target = self._find_target(zombies)
        if target:
            self.angle = math.atan2(target.y - self.y, target.x - self.x)
            bullets.append(Bullet(self.x, self.y, target,
                                  self.bullet_speed, int(self.damage * damage_mul),
                                  self.bullet_color, self.splash, self.slow))
            self.cooldown = self.fire_rate

    def _find_target(self, zombies):
        best, best_prog = None, -1
        for z in zombies:
            d = math.hypot(z.x - self.x, z.y - self.y)
            if d <= self.range and z.progress > best_prog:
                best_prog, best = z.progress, z
        return best

    def draw(self, surface, selected=False, shake=(0, 0)):
        cx, cy = self.x + shake[0], self.y + shake[1]
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


class SmashEffect:
    """Animation for tower placement with draw-out, draw-in, and smash phases."""
    def __init__(self, x, y, tower_type):
        self.x, self.y = x, y
        self.tower_type = tower_type
        self.max_timer = 28  # duration in frames
        self.timer = self.max_timer
        self.color = TOWER_TYPES[tower_type]["color"]
        self.particles = None

    def _generate_particles(self):
        self.particles = []
        num_particles = 22
        for i in range(num_particles):
            angle = (i / num_particles) * math.pi * 2 + random.uniform(-0.4, 0.4)
            speed = random.uniform(6, 16)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed * 0.5 - random.uniform(1.5, 3.5)
            size = random.randint(2, 5)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'vx': vx,
                'vy': vy,
                'size': size,
                'life': 1.0
            })

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            return
        progress = 1 - (self.timer / self.max_timer)
        if progress >= 0.72 and self.particles is None:
            self._generate_particles()
        if self.particles is not None:
            for p in self.particles:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.35
                p['life'] -= 0.05

    def draw(self, surface, shake=(0, 0)):
        if self.timer <= 0:
            return
        progress = 1 - (self.timer / self.max_timer)
        cx = int(self.x) + shake[0]
        cy = int(self.y) + shake[1]

        if progress < 0.34:
            radius = 12 + progress * 90
            alpha = max(0, int(180 * (1 - progress)))
            pulse = pygame.Surface((int(radius * 2 + 4), int(radius * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(pulse, (*self.color, alpha), (int(radius + 2), int(radius + 2)), int(radius), 2)
            surface.blit(pulse, (cx - int(radius) - 2, cy - int(radius) - 2))
            for i in range(7):
                angle = (i / 7) * math.pi * 2
                line_len = 16 + progress * 42
                x2 = cx + math.cos(angle) * line_len
                y2 = cy + math.sin(angle) * line_len
                pygame.draw.line(surface, (*self.color, 220), (cx, cy), (x2, y2), 2)
            glow = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, 120), (12, 12), 10)
            surface.blit(glow, (cx - 12, cy - 12))

        elif progress < 0.7:
            phase = (progress - 0.34) / 0.36
            ring_radius = 70 - phase * 46
            ring_alpha = max(0, int(220 * (1 - phase)))
            ring = pygame.Surface((int(ring_radius * 2 + 4), int(ring_radius * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*self.color, ring_alpha), (int(ring_radius + 2), int(ring_radius + 2)), int(ring_radius), 4)
            surface.blit(ring, (cx - int(ring_radius) - 2, cy - int(ring_radius) - 2))
            inward_alpha = max(0, int(200 * (1 - phase)))
            for i in range(8):
                angle = (i / 8) * math.pi * 2
                x2 = cx + math.cos(angle) * ring_radius
                y2 = cy + math.sin(angle) * ring_radius
                pygame.draw.line(surface, (*self.color, inward_alpha), (int(x2), int(y2)), (cx, cy), 2)
            glow = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, 170), (14, 14), 12)
            surface.blit(glow, (cx - 14, cy - 14))

        else:
            smash_phase = (progress - 0.7) / 0.3
            smash_radius = 40 + smash_phase * 70
            smash_alpha = max(0, int(220 * (1 - smash_phase)))
            if self.particles is not None:
                for p in self.particles:
                    if p['life'] > 0:
                        alpha = int(255 * p['life'])
                        particle_surf = pygame.Surface((p['size'] * 2 + 2, p['size'] * 2 + 2), pygame.SRCALPHA)
                        particle_color = tuple(max(0, c - 40) for c in self.color)
                        pygame.draw.circle(particle_surf, (*particle_color, alpha), (p['size'] + 1, p['size'] + 1), p['size'])
                        surface.blit(particle_surf, (int(p['x'] - p['size'] - 1) + shake[0], int(p['y'] - p['size'] - 1) + shake[1]))
            impact = pygame.Surface((int(smash_radius * 2 + 6), int(smash_radius * 2 + 6)), pygame.SRCALPHA)
            pygame.draw.circle(impact, (*self.color, smash_alpha), (int(smash_radius + 3), int(smash_radius + 3)), int(smash_radius), 3)
            surface.blit(impact, (cx - int(smash_radius) - 3, cy - int(smash_radius) - 3))
            core_alpha = max(0, int(200 * (1 - smash_phase * 0.5)))
            core = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(core, (*self.color, core_alpha), (20, 20), 16)
            surface.blit(core, (cx - 20, cy - 20))
            for i in range(5):
                angle = (i / 5) * math.pi * 2 + smash_phase * 0.8
                offset = 26 + smash_phase * 20
                x2 = cx + math.cos(angle) * offset
                y2 = cy + math.sin(angle) * offset
                pygame.draw.line(surface, (*self.color, max(0, smash_alpha - 60)), (cx, cy), (x2, y2), 2)


class MoneyLossEffect:
    def __init__(self, x, y, amount):
        self.x = x
        self.y = y
        self.amount = amount
        self.timer = 40
        self.max_timer = 40

    def update(self):
        self.timer -= 1

    def draw(self, surface, shake=(0, 0)):
        if self.timer <= 0:
            return
        progress = 1 - (self.timer / self.max_timer)
        rise = int(progress * 42)
        alpha = int(220 * (1 - progress))
        txt = MONEY_LOSS_FONT.render(f"-{self.amount} kr", True, (255, 200, 120))
        txt.set_alpha(alpha)
        badge_w = txt.get_width() + 16
        badge_h = txt.get_height() + 10
        bx = self.x - badge_w // 2 + shake[0]
        by = self.y - rise + shake[1]
        badge = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        badge.fill((30, 24, 20, alpha))
        pygame.draw.rect(badge, (220, 200, 120, alpha), (0, 0, badge_w, badge_h), 1)
        surface.blit(badge, (bx, by))
        surface.blit(txt, (bx + 8, by + 5))


class SplashEffect:
    def __init__(self, x, y, radius, big=False):
        self.x, self.y = x, y
        self.radius    = radius
        self.timer     = 30 if big else 20
        self.max_timer = self.timer
        self.big       = big

    def update(self):
        self.timer -= 1

    def draw(self, surface, shake=(0, 0)):
        frac = self.timer / self.max_timer
        r = int(self.radius * (1 - frac) + 6)
        if self.big:
            col = (255, int(160 * frac), 0)
            pygame.draw.circle(surface, col,    (int(self.x) + shake[0], int(self.y) + shake[1]), r,           4)
            pygame.draw.circle(surface, YELLOW, (int(self.x) + shake[0], int(self.y) + shake[1]), max(1,r-6),  2)
        else:
            pygame.draw.circle(surface, ORANGE, (int(self.x) + shake[0], int(self.y) + shake[1]), r, 2)


class KillEffect:
    def __init__(self, x, y, ztype):
        self.x = x
        self.y = y
        self.timer = 24
        self.max_timer = 24
        base_color = ZOMBIE_STATS.get(ztype, {}).get("color", (255, 190, 50))
        self.color = tuple(min(255, int(c * 1.2)) for c in base_color)
        self.particles = []
        for i in range(14):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2.5, 6.0)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(2, 5),
                'life': 1.0,
            })

    def update(self):
        self.timer -= 1
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.2
            p['life'] -= 0.06

    def draw(self, surface, shake=(0, 0)):
        if self.timer <= 0:
            return
        progress = 1 - (self.timer / self.max_timer)
        cx = int(self.x) + shake[0]
        cy = int(self.y) + shake[1]
        ring_r = int(20 + progress * 28)
        alpha = int(180 * (1 - progress))
        ring = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*self.color, alpha), (ring_r + 2, ring_r + 2), ring_r, 3)
        surface.blit(ring, (cx - ring_r - 2, cy - ring_r - 2))
        for p in self.particles:
            if p['life'] > 0:
                particle_surf = pygame.Surface((p['size']*2 + 2, p['size']*2 + 2), pygame.SRCALPHA)
                col = tuple(min(255, int(c * 1.1)) for c in self.color)
                pygame.draw.circle(particle_surf, (*col, int(255 * p['life'])), (p['size'] + 1, p['size'] + 1), p['size'])
                surface.blit(particle_surf, (int(p['x'] - p['size']) + shake[0], int(p['y'] - p['size']) + shake[1]))


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


# ── Vapendel på kartan ────────────────────────────────────────────────────────
class WeaponPart:
    """En vapendel som blinkar på kartan under spelet."""
    RADIUS = 11

    def __init__(self, col, row, ptype):
        self.col      = col
        self.row      = row
        self.ptype    = ptype
        self.x        = col * GRID_SIZE + GRID_SIZE // 2
        self.y        = row * GRID_SIZE + GRID_SIZE // 2
        self.timer    = 0
        self.lifetime = 720    # ~12 s vid 60 fps

    def update(self):
        self.timer    += 1
        self.lifetime -= 1

    @property
    def alive(self):
        return self.lifetime > 0

    @property
    def visible(self):
        period = 8 if self.lifetime < 120 else 22
        return (self.timer // period) % 2 == 0

    def draw(self, surface, shake=(0, 0)):
        if not self.visible:
            return
        data  = PART_TYPES[self.ptype]
        color = data["color"]
        px    = self.x + shake[0]
        py    = self.y + shake[1]
        pulse = abs(math.sin(self.timer * 0.07))
        glow_r = int(16 + pulse * 8)
        glow_surf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, int(60 + pulse * 80)),
                           (glow_r + 2, glow_r + 2), glow_r)
        surface.blit(glow_surf, (px - glow_r - 2, py - glow_r - 2))
        pygame.draw.circle(surface, color, (px, py), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (px, py), self.RADIUS, 2)
        lbl = PART_FONT.render(data["name"][0], True, (20, 20, 20))
        surface.blit(lbl, (px - lbl.get_width() // 2, py - lbl.get_height() // 2))

    def hit(self, mx, my):
        return (mx - self.x) ** 2 + (my - self.y) ** 2 <= (self.RADIUS + 10) ** 2


# ── Spelet ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        # Start in fullscreen mode and adapt layout to actual display size
        global SCREEN_W, SCREEN_H, COLS, ROWS
        self.fullscreen = True
        flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
        # Use (0,0) so Pygame picks the current display resolution for fullscreen
        self.screen = pygame.display.set_mode((0, 0), flags)
        global SCREEN_W, SCREEN_H, COLS, ROWS
        w, h = self.screen.get_size()
        SCREEN_W, SCREEN_H = w, h
        COLS = SCREEN_W // GRID_SIZE
        ROWS = (SCREEN_H - 144) // GRID_SIZE
        pygame.display.set_caption("MineBattle – LKAB Gruvförsvar")
        self.clock      = pygame.time.Clock()
        self.show_menu  = False
        self.paused     = False
        self.font_big   = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 13, bold=True)
        self.ui_font    = pygame.font.SysFont("Arial", 16, bold=True)
        self.splash_image = None
        try:
            self.splash_image = pygame.image.load(os.path.join(MEDIA_DIR, "Gemini_Generated_Image_y20g1jy20g1jy20g.png")).convert()
        except Exception:
            self.splash_image = None
        self.map_seed   = random.randint(0, 999_999)
        self.rng        = random.Random(self.map_seed)
        self.level      = 1
        self._init_level()
        self.total_waves_done = 0   # för upplåsning av torn
        self.money = 300
        self.lives = 20
        self.score = 0
        self.weapon_click_sound = None
        self.screen_shake_timer = 0  # camera shake effect
        self.screen_shake_intensity = 0
        self.current_shake_x = 0
        self.current_shake_y = 0
        self._reset_wave_state()
        self.load_background_music()
        # UI animation state for hover/press smoothing
        self.ui_state = {
            'towers': {k: {'hover': 0.0, 'press': 0.0} for k in TOWER_TYPES.keys()},
            'wave_hover': 0.0,
            'wave_press': 0.0,
        }
        # big countdown font
        self.count_font = pygame.font.SysFont("Arial", 96, bold=True)
        self.show_intro = True
        self.speed_multiplier = 1.0
        self.play_intro_music()

    def _init_level(self):
        self.waypoints  = generate_procedural_waypoints(self.level, self.rng)
        self.path_cells = build_path_cells(self.waypoints)
        # Bakgrundstexturen randomizas med samma seed som banan
        bg_seed = self.map_seed * 7 + self.level * 99
        self.bg_surface = make_mine_background(
            random.Random(bg_seed), self.path_cells, self.level, self.waypoints)

    def load_background_music(self):
        self.placement_music_sound = None
        self.placement_music_channel = None
        self.placement_music_loaded = False
        self.placement_music_volume = 0.38
        self.placement_music_fade_target = 0.0
        self.placement_music_fade_speed = 0.1
        try:
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(0.0)
            self.placement_music_loaded = True
        except Exception as e:
            print(f"Background music could not be loaded: {MUSIC_FILE} - {e}")
            try:
                self.placement_music_sound = pygame.mixer.Sound(MUSIC_FILE)
                self.placement_music_sound.set_volume(0.0)
            except Exception as e2:
                print(f"Background sound fallback failed: {e2}")

        self.weapon_click_sound = None
        self.placement_sound = None
        self.intro_sound = None
        self.intro_channel = None
        self.boom_sound = None
        try:
            if os.path.exists(CLICK_SOUND_FILE):
                self.weapon_click_sound = pygame.mixer.Sound(CLICK_SOUND_FILE)
            else:
                self.weapon_click_sound = make_placement_sound()
        except Exception:
            self.weapon_click_sound = make_placement_sound()

        try:
            if os.path.exists(STAMP_SOUND_FILE):
                self.placement_sound = pygame.mixer.Sound(STAMP_SOUND_FILE)
            else:
                self.placement_sound = make_placement_sound()
        except Exception:
            self.placement_sound = make_placement_sound()

        try:
            if os.path.exists(INTRO_FILE):
                self.intro_sound = pygame.mixer.Sound(INTRO_FILE)
            else:
                self.intro_sound = None
        except Exception:
            self.intro_sound = None

        try:
            if os.path.exists(BOOM_SOUND_FILE):
                self.boom_sound = pygame.mixer.Sound(BOOM_SOUND_FILE)
            else:
                self.boom_sound = None
        except Exception:
            self.boom_sound = None

        # play music only when placing towers, not immediately

        # Load wave-related sounds if available
        try:
            if os.path.exists(HORN_FILE):
                self.horn_sound = pygame.mixer.Sound(HORN_FILE)
            else:
                self.horn_sound = None
        except Exception:
            self.horn_sound = None
        try:
            if os.path.exists(CYBER_FILE):
                self.cyber_sound = pygame.mixer.Sound(CYBER_FILE)
            else:
                self.cyber_sound = None
        except Exception:
            self.cyber_sound = None

    def play_placement_music(self):
        self.placement_music_fade_target = 0.38
        if self.placement_music_sound:
            if not self.placement_music_channel or not self.placement_music_channel.get_busy():
                self.placement_music_channel = self.placement_music_sound.play(-1)
        elif self.placement_music_loaded:
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            except Exception:
                pass

    def stop_placement_music(self):
        self.placement_music_fade_target = 0.0

    def update_music_fade(self):
        current_vol = pygame.mixer.music.get_volume() if self.placement_music_loaded else (self.placement_music_sound.get_volume() if self.placement_music_sound else 0.0)
        if current_vol < self.placement_music_fade_target:
            current_vol = min(self.placement_music_fade_target, current_vol + self.placement_music_fade_speed * 0.016)
        elif current_vol > self.placement_music_fade_target:
            current_vol = max(self.placement_music_fade_target, current_vol - self.placement_music_fade_speed * 0.016)
        
        if self.placement_music_loaded:
            pygame.mixer.music.set_volume(current_vol)
        elif self.placement_music_sound:
            self.placement_music_sound.set_volume(current_vol)
        
        if current_vol <= 0.0 and self.placement_music_fade_target == 0.0:
            if self.placement_music_channel:
                try:
                    self.placement_music_channel.stop()
                except Exception:
                    pass
            elif self.placement_music_loaded:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass

    def play_intro_music(self):
        if self.intro_sound and not self.intro_channel:
            try:
                self.intro_channel = self.intro_sound.play(-1)
            except Exception:
                self.intro_channel = None

    def stop_intro_music(self):
        if self.intro_channel:
            try:
                self.intro_channel.stop()
            except Exception:
                pass
            self.intro_channel = None
            self.placement_music_channel = None
        elif self.placement_music_loaded:
            try:
                pygame.mixer.music.pause()
            except Exception:
                pass

    def stop_cyber_music(self):
        if getattr(self, 'cyber_channel', None):
            try:
                self.cyber_channel.stop()
            except Exception:
                pass
            self.cyber_channel = None

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)

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
        # countdown state for scheduled wave start
        self.wave_countdown = 0
        self.wave_countdown_timer = 0.0
        self.wave_countdown_number = 0
        self.cyber_channel = None
        # wave progress bar
        self.wave_bar_total = 0
        self.wave_bar_remaining = 0
        # vapendelar
        self.parts_on_map      = []
        self.collected_parts   = []
        self.assembled_items   = []
        self.free_tower_queue  = []
        self.damage_boost_waves = 0
        self.show_assembly     = False

    def full_reset(self):
        self.level            = 1
        self.total_waves_done = 0
        self.money = 300
        self.lives = 20
        self.score = 0
        # Ny slumpad seed → ny bana varje omstart
        self.map_seed = random.randint(0, 999_999)
        self.rng      = random.Random(self.map_seed)
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
        # schedule a 3..1 countdown before starting the wave
        if self.wave_active:
            return
        waves = LEVEL_WAVES[self.level]
        if self.wave >= len(waves):
            return
        if self.wave_countdown > 0:
            return
        self.wave_countdown = 3
        self.wave_countdown_number = 3
        self.wave_countdown_timer = 1.0
        # set wave progress bar to full for upcoming wave
        try:
            total = sum(group.get("count", 0) for group in waves[self.wave])
        except Exception:
            total = 0
        self.wave_bar_total = total
        self.wave_bar_remaining = total
        # pause placement music while countdown and wave are about to start
        self.stop_placement_music()
        try:
            if getattr(self, 'horn_sound', None):
                self.horn_sound.play()
        except Exception:
            pass

    def _spawn_wave_parts(self):
        """Spawna 1-3 vapendelar på slumpmässiga lediga celler."""
        n = random.randint(1, 3)
        free = [
            (c, r) for c in range(COLS) for r in range(ROWS)
            if (c, r) not in self.path_cells
            and not any(t.col == c and t.row == r for t in self.towers)
            and not any(p.col == c and p.row == r for p in self.parts_on_map)
        ]
        random.shuffle(free)
        ptypes = list(PART_TYPES.keys())
        for c, r in free[:n]:
            self.parts_on_map.append(WeaponPart(c, r, random.choice(ptypes)))

    def _start_wave_immediate(self):
        waves = LEVEL_WAVES[self.level]
        if self.wave >= len(waves):
            return
        self.wave_active   = True
        self.between_waves = False
        self.show_assembly = False
        self.spawn_queue   = []
        for group in waves[self.wave]:
            for _ in range(group["count"]):
                self.spawn_queue.append((group["type"], group["interval"]))
        self.spawn_timer = 0
        self.wave += 1
        # Spawna nya vapendelar för den här vågen
        self.parts_on_map = []
        self._spawn_wave_parts()
        # start cyber track now that the wave is active
        self.stop_cyber_music()
        if getattr(self, 'cyber_sound', None):
            try:
                self.cyber_channel = self.cyber_sound.play(-1)
            except Exception:
                self.cyber_channel = None

    def handle_spawn(self):
        if not self.wave_active or not self.spawn_queue:
            if self.wave_active and not self.spawn_queue and not self.zombies:
                self.wave_active  = False
                self.between_waves = True
                self.wave_complete_timer = 120
                bonus = 50 + self.wave * 10
                self.money += bonus
                self.total_waves_done += 1
                self.stop_cyber_music()
                if not self.level_complete and not self.game_over:
                    self.play_placement_music()
                # Upplåsningsbanners
                if self.total_waves_done in UNLOCK_MESSAGES:
                    self.banners.append(UnlockBanner(UNLOCK_MESSAGES[self.total_waves_done]))
                # Vapendel-skadaboost minskar en våg
                if self.damage_boost_waves > 0:
                    self.damage_boost_waves -= 1
                # Nivå klar?
                if self.wave >= len(LEVEL_WAVES[self.level]):
                    self.level_complete = True
            return
        self.spawn_timer -= self.speed_multiplier
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
        # Kolla gratis-kö INNAN unlock-kontroll – smidda torn är alltid tillåtna
        free_placement = (self.selected_tower_type in self.free_tower_queue)
        if not free_placement and not self.tower_unlocked(self.selected_tower_type):
            return
        if self.grid_occupied(col, row):
            return
        cost = 0 if free_placement else tdata["cost"]
        if self.money < cost:
            return
        tower = Tower(col, row, self.selected_tower_type)
        self.towers.append(tower)
        self.money -= cost
        if free_placement:
            self.free_tower_queue.remove(self.selected_tower_type)
        # Add smash effect when tower is placed
        self.effects.append(SmashEffect(tower.x, tower.y, self.selected_tower_type))
        mx, my = pygame.mouse.get_pos()
        if cost > 0:
            self.effects.append(MoneyLossEffect(mx, my - 28, cost))
        if self.placement_sound:
            self.placement_sound.play()
        elif self.weapon_click_sound:
            self.weapon_click_sound.play()

    def update(self, dt=0.0):
        if self.game_over or self.level_transition or self.level_complete:
            return
        # Update music fade
        self.update_music_fade()
        # Update camera shake
        if self.screen_shake_timer > 0:
            self.current_shake_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            self.current_shake_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            self.screen_shake_timer -= 1
        else:
            self.current_shake_x = 0
            self.current_shake_y = 0
        self.handle_spawn()
        # Uppdatera vapendelar
        for p in self.parts_on_map:
            p.update()
        self.parts_on_map = [p for p in self.parts_on_map if p.alive]
        for z in self.zombies:
            z.update(self.speed_multiplier)
        for z in self.zombies:
            if z.reached_end:
                self.lives -= 1
        self.zombies = [z for z in self.zombies if z.alive and not z.reached_end]
        dmul = 2.0 if self.damage_boost_waves > 0 else 1.0
        for t in self.towers:
            t.update(self.zombies, self.bullets, self.speed_multiplier, dmul)
        for b in self.bullets:
            b.update(self.zombies, self.speed_multiplier)
            if b.splash > 0 and not b.alive:
                self.effects.append(SplashEffect(b.x, b.y, b.splash, big=(b.splash >= 80)))
        self.bullets = [b for b in self.bullets if b.alive]
        for z in [z for z in self.zombies if not z.alive]:
            self.money += z.reward
            self.score += z.reward
            # show kill feedback when the enemy dies
            if not z.reached_end:
                self.effects.append(KillEffect(z.x, z.y, z.ztype))
                if self.boom_sound:
                    self.boom_sound.play()
            # decrement wave progress when an enemy is killed
            if self.wave_bar_total > 0 and self.wave_bar_remaining > 0:
                self.wave_bar_remaining = max(0, self.wave_bar_remaining - 1)
        self.zombies = [z for z in self.zombies if z.alive]
        for e in self.effects:
            e.update()
        self.effects = [e for e in self.effects if getattr(e, 'timer', 1) > 0]
        if self.wave_complete_timer > 0:
            self.wave_complete_timer -= self.speed_multiplier
        if self.lives <= 0:
            self.game_over = True
        # UI animations (hover/press smoothing)
        mx, my = pygame.mouse.get_pos()
        # Towers
        button_count = len(TOWER_TYPES)
        tower_spacing = 132
        tower_cy = ROWS * GRID_SIZE + 106
        total_width = button_count * tower_spacing
        start_x = SCREEN_W - 80 - total_width + tower_spacing // 2
        for i, ttype in enumerate(TOWER_TYPES.keys()):
            cx = start_x + i * tower_spacing
            cy = tower_cy
            radius = 46
            hovered = (mx - cx) ** 2 + (my - cy) ** 2 <= (radius + 8) ** 2
            s = self.ui_state['towers'][ttype]
            target = 1.0 if hovered else 0.0
            s['hover'] += (target - s['hover']) * min(1.0, dt * 10.0)
            s['press'] = max(0.0, s['press'] - dt * 6.0)
        # Wave button hover/press
        ui_y = ROWS * GRID_SIZE
        panel_h = SCREEN_H - ui_y
        cx_btn = SCREEN_W // 2
        cy_btn = ui_y + 48
        radius = 52
        wh = ((mx - cx_btn) ** 2 + (my - cy_btn) ** 2 <= radius ** 2)
        self.ui_state['wave_hover'] += ((1.0 if wh else 0.0) - self.ui_state['wave_hover']) * min(1.0, dt * 8.0)
        self.ui_state['wave_press'] = max(0.0, self.ui_state['wave_press'] - dt * 6.0)
        # handle countdown scheduling
        if self.wave_countdown > 0:
            self.wave_countdown_timer -= dt
            if self.wave_countdown_timer <= 0:
                # move to next countdown number or start wave
                if self.wave_countdown_number > 1:
                    self.wave_countdown_number -= 1
                    self.wave_countdown_timer = 1.0
                else:
                    # stop cyber buildup loop and go live
                    try:
                        if self.cyber_channel:
                            self.cyber_channel.stop()
                            self.cyber_channel = None
                    except Exception:
                        self.cyber_channel = None
                    self.wave_countdown = 0
                    self.wave_countdown_timer = 0.0
                    self.wave_countdown_number = 0
                    self._start_wave_immediate()

    # ── Vapendelar – hjälpmetoder ──────────────────────────────────────────────
    def _assembly_btn_rect(self):
        ui_y = ROWS * GRID_SIZE
        return pygame.Rect(SCREEN_W // 2 - 200, ui_y + 14, 88, 32)

    def _can_craft(self, recipe):
        inv = list(self.collected_parts)
        for part in recipe["parts"]:
            if part in inv:
                inv.remove(part)
            else:
                return False
        return True

    def _craft_recipe(self, recipe):
        inv = list(self.collected_parts)
        for part in recipe["parts"]:
            inv.remove(part)
        self.collected_parts = inv
        effect = recipe["effect"]
        if effect == "money":
            self.money += recipe["amount"]
            self.score += recipe["amount"]
        elif effect == "damage_boost":
            self.damage_boost_waves += 1
        elif effect == "free_tower":
            self.free_tower_queue.append(recipe["tower"])
            # Välj torntypen automatiskt och stäng panelen – klicka bara på kartan!
            self.selected_tower_type = recipe["tower"]
            self.show_assembly = False

    def _handle_assembly_click(self, mx, my):
        popup_x = 18
        popup_y = max(10, ROWS * GRID_SIZE - 330)
        popup_w = 380
        close_rect = pygame.Rect(popup_x + popup_w - 32, popup_y + 6, 26, 26)
        if close_rect.collidepoint(mx, my):
            self.show_assembly = False
            return True
        recipe_y = popup_y + 94
        for recipe in PART_RECIPES:
            btn = pygame.Rect(popup_x + 8, recipe_y, popup_w - 16, 52)
            if btn.collidepoint(mx, my) and self._can_craft(recipe):
                self._craft_recipe(recipe)
                return True
            recipe_y += 58
        return False

    def draw_parts_on_map(self):
        for p in self.parts_on_map:
            p.draw(self.screen, shake=(self.current_shake_x, self.current_shake_y))

    def draw_assembly_ui(self):
        if not self.show_assembly:
            return
        popup_x = 18
        popup_y = max(10, ROWS * GRID_SIZE - 330)
        popup_w = 380
        popup_h = 100 + len(PART_RECIPES) * 58 + 12

        # Background panel
        surf = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
        surf.fill((16, 14, 12, 235))
        pygame.draw.rect(surf, (175, 150, 90), (0, 0, popup_w, popup_h), 2, border_radius=12)
        self.screen.blit(surf, (popup_x, popup_y))

        # Title
        title = self.font_big.render("SMIDESBORD", True, WARN_YELLOW)
        self.screen.blit(title, (popup_x + 12, popup_y + 10))

        # Close button
        close_rect = pygame.Rect(popup_x + popup_w - 32, popup_y + 6, 26, 26)
        pygame.draw.rect(self.screen, (180, 45, 45), close_rect, border_radius=6)
        cx_t = self.font_med.render("X", True, WHITE)
        self.screen.blit(cx_t, (close_rect.x + 6, close_rect.y + 3))

        # Inventory row
        inv_lbl = self.font_small.render("Dina delar:", True, (200, 200, 180))
        self.screen.blit(inv_lbl, (popup_x + 12, popup_y + 46))
        for i, ptype in enumerate(self.collected_parts[:8]):
            color = PART_TYPES[ptype]["color"]
            cx2 = popup_x + 110 + i * 28
            cy2 = popup_y + 54
            pygame.draw.circle(self.screen, color, (cx2, cy2), 11)
            pygame.draw.circle(self.screen, WHITE, (cx2, cy2), 11, 1)
            lbl = PART_FONT.render(PART_TYPES[ptype]["name"][0], True, (20, 20, 20))
            self.screen.blit(lbl, (cx2 - lbl.get_width() // 2, cy2 - lbl.get_height() // 2))
        if not self.collected_parts:
            no_lbl = self.font_small.render("(inga delar samlade ännu)", True, GRAY)
            self.screen.blit(no_lbl, (popup_x + 110, popup_y + 46))

        # Separator
        pygame.draw.line(self.screen, (100, 88, 65),
                         (popup_x + 8, popup_y + 72), (popup_x + popup_w - 8, popup_y + 72), 1)
        recipe_lbl = self.font_small.render("Recept:", True, (200, 200, 180))
        self.screen.blit(recipe_lbl, (popup_x + 12, popup_y + 76))

        # Recipe buttons
        recipe_y = popup_y + 94
        for recipe in PART_RECIPES:
            can_craft = self._can_craft(recipe)
            btn_rect = pygame.Rect(popup_x + 8, recipe_y, popup_w - 16, 52)
            bg_col = (30, 55, 30) if can_craft else (26, 22, 20)
            border_col = (80, 200, 80) if can_craft else (75, 65, 55)
            pygame.draw.rect(self.screen, bg_col, btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_col, btn_rect, 1, border_radius=8)

            # Part icons for recipe
            px2 = btn_rect.x + 10
            for j, ptype in enumerate(recipe["parts"]):
                color = PART_TYPES[ptype]["color"]
                ccx = px2 + 11 + j * 26
                ccy = btn_rect.y + btn_rect.h // 2
                pygame.draw.circle(self.screen, color, (ccx, ccy), 10)
                pygame.draw.circle(self.screen, WHITE, (ccx, ccy), 10, 1)
                part_lbl = PART_FONT.render(PART_TYPES[ptype]["name"][0], True, (20, 20, 20))
                self.screen.blit(part_lbl, (ccx - part_lbl.get_width() // 2, ccy - part_lbl.get_height() // 2))

            # Arrow and text
            ax = px2 + len(recipe["parts"]) * 26 + 16
            arr = self.font_small.render("->", True, (180, 180, 180))
            self.screen.blit(arr, (ax, btn_rect.y + 8))
            name_col = WHITE if can_craft else GRAY
            name_txt = self.font_med.render(recipe["name"], True, name_col)
            self.screen.blit(name_txt, (ax + 22, btn_rect.y + 6))
            desc_col = (190, 190, 160) if can_craft else DARK_GRAY
            desc_txt = self.font_small.render(recipe["desc"], True, desc_col)
            self.screen.blit(desc_txt, (ax + 22, btn_rect.y + 28))
            recipe_y += 58

    # ── Ritning ───────────────────────────────────────────────────────────────
    def draw_map(self):
        shake_x = self.current_shake_x
        shake_y = self.current_shake_y
        self.screen.blit(self.bg_surface, (shake_x, shake_y))
        for c, r in self.path_cells:
            x, y = c * GRID_SIZE + shake_x, r * GRID_SIZE + shake_y
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
        self.screen.blit(s, (sx - s.get_width()//2 + shake_x, sy-7 + shake_y))
        self.screen.blit(e, (ex - e.get_width()//2 + shake_x, ey-7 + shake_y))

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

    def draw_wave_progress(self):
        if not getattr(self, 'wave_bar_total', 0):
            return
        # top-center wave progress bar
        bar_w = min(600, SCREEN_W - 200)
        bar_h = 14
        x = SCREEN_W // 2 - bar_w // 2
        y = 28
        rect_bg = pygame.Rect(x, y, bar_w, bar_h)
        # background
        pygame.draw.rect(self.screen, (40, 40, 40, 200), rect_bg)
        # border
        pygame.draw.rect(self.screen, (220, 210, 180), rect_bg, 2)
        # fill proportional to remaining enemies
        if self.wave_bar_total > 0:
            frac = max(0.0, min(1.0, self.wave_bar_remaining / float(self.wave_bar_total)))
        else:
            frac = 0.0
        fill_w = int(bar_w * frac)
        if fill_w > 0:
            pygame.draw.rect(self.screen, (80, 200, 120), (x, y, fill_w, bar_h))
        # label
        lbl = self.font_small.render(f"Vågprogress: {self.wave_bar_total - self.wave_bar_remaining}/{self.wave_bar_total}", True, WHITE)
        self.screen.blit(lbl, (x + bar_w//2 - lbl.get_width()//2, y - lbl.get_height() - 4))

    def draw_ui(self):
        ui_y = ROWS * GRID_SIZE
        panel_h = SCREEN_H - ui_y
        # Frosted bottom panel
        panel_surf = pygame.Surface((SCREEN_W, panel_h), pygame.SRCALPHA)
        panel_surf.fill((20, 18, 22, 200))
        pygame.draw.rect(panel_surf, (255, 255, 255, 18), panel_surf.get_rect(), 2, border_radius=26)
        self.screen.blit(panel_surf, (0, ui_y))

        # centered wave/start button
        wave_cx = SCREEN_W // 2
        wave_cy = ui_y + 62
        btn_r = 66
        wh = self.ui_state['wave_hover']
        wp = self.ui_state['wave_press']
        scale = 1.0 + wh * 0.18 - wp * 0.08
        r = int(btn_r * scale)
        if self.between_waves and not self.level_complete:
            glow = pygame.Surface((r * 2 + 32, r * 2 + 32), pygame.SRCALPHA)
            glow_color = (200, 90, 120, int(140 + wh * 80))
            pygame.draw.circle(glow, glow_color, (r + 16, r + 16), r + 12)
            self.screen.blit(glow, (wave_cx - r - 16, wave_cy - r - 16))
            pygame.draw.circle(self.screen, (24, 24, 26), (wave_cx, wave_cy), r)
            pygame.draw.circle(self.screen, (240, 220, 180), (wave_cx, wave_cy), r, 5)
            label = "REDO"
            subtitle = f"Våg {min(self.wave+1, len(LEVEL_WAVES[self.level]))}"
            txt = self.font_big.render(label, True, WHITE)
            sub = self.font_med.render(subtitle, True, (230, 230, 230))
            self.screen.blit(txt, (wave_cx - txt.get_width() // 2, wave_cy - txt.get_height() // 2 - 8))
            self.screen.blit(sub, (wave_cx - sub.get_width() // 2, wave_cy + txt.get_height() // 2 - 2))
            # Smidesbord-knapp
            abtn = self._assembly_btn_rect()
            abtn_col = (50, 140, 50) if self.show_assembly else (40, 55, 40)
            abtn_border = (120, 220, 120) if self.show_assembly else (90, 110, 80)
            pygame.draw.rect(self.screen, abtn_col, abtn, border_radius=8)
            pygame.draw.rect(self.screen, abtn_border, abtn, 1, border_radius=8)
            part_count = len(self.collected_parts)
            atxt = self.font_small.render(f"SMIDE ({part_count})", True, WHITE)
            self.screen.blit(atxt, (abtn.x + abtn.w // 2 - atxt.get_width() // 2,
                                    abtn.y + abtn.h // 2 - atxt.get_height() // 2))

        # Gratis-torn indikator
        if self.free_tower_queue:
            ft = self.free_tower_queue[0]
            ft_col = TOWER_TYPES[ft]["color"]
            ft_txt = self.font_small.render(f"GRATIS: {TOWER_TYPES[ft]['name']} – välj och placera!", True, ft_col)
            bw = ft_txt.get_width() + 16
            bh = ft_txt.get_height() + 8
            bx = SCREEN_W // 2 - bw // 2
            by = ui_y - bh - 4
            bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bg.fill((20, 20, 20, 200))
            pygame.draw.rect(bg, ft_col, (0, 0, bw, bh), 1, border_radius=6)
            self.screen.blit(bg, (bx, by))
            self.screen.blit(ft_txt, (bx + 8, by + 4))

        # Skadaboost-indikator
        if self.damage_boost_waves > 0:
            boost_txt = self.font_med.render(
                f"SKADABOOST x2  ({self.damage_boost_waves} vag kvar)", True, WARN_YELLOW)
            bw2 = boost_txt.get_width() + 16
            bh2 = boost_txt.get_height() + 8
            bx2 = SCREEN_W // 2 - bw2 // 2
            by2 = ui_y - bh2 - (36 if self.free_tower_queue else 4)
            bg2 = pygame.Surface((bw2, bh2), pygame.SRCALPHA)
            bg2.fill((50, 40, 10, 210))
            pygame.draw.rect(bg2, WARN_YELLOW, (0, 0, bw2, bh2), 1, border_radius=6)
            self.screen.blit(bg2, (bx2, by2))
            self.screen.blit(boost_txt, (bx2 + 8, by2 + 4))

        # left status section
        stats = [
            (f"{self.lives}", RED, "LIV"),
            (f"{self.money}", YELLOW, "KR"),
            (f"{self.wave}/{len(LEVEL_WAVES[self.level])}", WHITE, "VÅG"),
            (f"{self.score}", LIGHT_YELLOW, "POÄNG"),
        ]
        stat_radius = 54
        stat_spacing = stat_radius * 2 + 18
        stat_x = 80 + stat_radius
        stat_y = ui_y + 106
        for idx, (value, col, label) in enumerate(stats):
            cx = stat_x + idx * stat_spacing
            cy = stat_y
            stat_surf = pygame.Surface((stat_radius*2+12, stat_radius*2+12), pygame.SRCALPHA)
            pygame.draw.circle(stat_surf, (28, 28, 30, 220), (stat_radius+6, stat_radius+6), stat_radius)
            pygame.draw.circle(stat_surf, (*col, 200), (stat_radius+6, stat_radius+6), stat_radius-8)
            pygame.draw.circle(stat_surf, WHITE, (stat_radius+6, stat_radius+6), stat_radius, 4)
            self.screen.blit(stat_surf, (cx - stat_radius - 6, cy - stat_radius - 6))
            vtxt = self.font_big.render(value, True, WHITE)
            ltxt = self.font_med.render(label, True, WHITE)
            # text border
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.screen.blit(self.font_big.render(value, True, BLACK), (cx - vtxt.get_width() // 2 + ox, cy - 18 + oy))
                self.screen.blit(self.font_med.render(label, True, BLACK), (cx - ltxt.get_width() // 2 + ox, cy + 16 + oy))
            self.screen.blit(vtxt, (cx - vtxt.get_width() // 2, cy - 18))
            self.screen.blit(ltxt, (cx - ltxt.get_width() // 2, cy + 16))

        # right weapon selection section
        mx, my = pygame.mouse.get_pos()
        button_count = len(TOWER_TYPES)
        tower_cy = ui_y + 106
        tower_spacing = 132
        total_width = button_count * tower_spacing
        start_x = SCREEN_W - 80 - total_width + tower_spacing // 2
        for i, (ttype, data) in enumerate(TOWER_TYPES.items()):
            cx = start_x + i * tower_spacing
            cy = tower_cy
            unlocked = self.tower_unlocked(ttype)
            affordable = self.money >= data["cost"] and unlocked
            selected = self.selected_tower_type == ttype
            s = self.ui_state['towers'][ttype]
            hover_val = s['hover']
            press_val = s['press']
            base_rad = 46
            radius = int(base_rad + hover_val * 14 + (10 if selected else 0) - press_val * 8)
            color = data["color"] if affordable else (90, 90, 90)
            ring = pygame.Surface((radius*2+16, radius*2+16), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*color, 220), (radius+8, radius+8), radius)
            pygame.draw.circle(ring, (255,255,255,100), (radius+8, radius+8), radius, 5)
            pygame.draw.circle(ring, (255,255,255,20), (radius+8, radius+8), radius+8, 4)
            self.screen.blit(ring, (cx - radius - 8, cy - radius - 8))
            icon_col = WHITE if affordable else GRAY
            if hover_val > 0.12 or selected:
                label_text = ttype.capitalize()
                cost_text = f"{data['cost']} kr"
                txt = self.ui_font.render(label_text, True, WHITE)
                cost_txt = self.font_small.render(cost_text, True, WHITE if affordable else GRAY)
                bw = max(txt.get_width(), cost_txt.get_width()) + 22
                bh = txt.get_height() + cost_txt.get_height() + 22
                bx = cx - bw // 2
                by = cy - radius - bh - 14
                bubble = pygame.Surface((bw, bh), pygame.SRCALPHA)
                bubble.fill((18, 18, 20, 240))
                border = (255, 220, 160) if selected else (220, 220, 220)
                pygame.draw.rect(bubble, border, bubble.get_rect(), 2, border_radius=14)
                bubble.blit(txt, (11, 8))
                bubble.blit(cost_txt, (11, 8 + txt.get_height()))
                self.screen.blit(bubble, (bx, by))


    def draw_countdown(self):
        if self.wave_countdown <= 0 and self.wave_countdown_number <= 0:
            return
        # draw big number centered in map area
        overlay = pygame.Surface((SCREEN_W, ROWS * GRID_SIZE), pygame.SRCALPHA)
        overlay.fill((0,0,0,120))
        self.screen.blit(overlay, (0,0))
        n = max(1, self.wave_countdown_number)
        t = self.count_font.render(str(n), True, WHITE)
        x = SCREEN_W//2 - t.get_width()//2
        y = ROWS*GRID_SIZE//2 - t.get_height()//2
        self.screen.blit(t, (x, y))

    def draw_intro(self):
        if self.splash_image:
            splash = pygame.transform.smoothscale(self.splash_image, (SCREEN_W, SCREEN_H))
            self.screen.blit(splash, (0, 0))
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))
        else:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((6, 6, 6, 240))
            self.screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont("Arial", 82, bold=True)
        title = title_font.render("MINE BATTLE XP!", True, (255, 230, 180))
        shadow = title_font.render("MINE BATTLE XP!", True, (20, 20, 20))
        cx = SCREEN_W//2
        cy = SCREEN_H//2 - 52
        self.screen.blit(shadow, (cx - shadow.get_width()//2 + 4, cy - shadow.get_height()//2 + 6))
        self.screen.blit(title, (cx - title.get_width()//2, cy - title.get_height()//2))
        start_hint = pygame.font.SysFont("Arial", 44, bold=True).render("Tryck ENTER för att starta", True, (230, 230, 230))
        speed_hint = pygame.font.SysFont("Arial", 44, bold=True).render("Håll SPACE för x2 hastighet under spelet", True, (210, 210, 210))
        exit_hint = pygame.font.SysFont("Arial", 44, bold=True).render("ESC för att avsluta spelet", True, (210, 210, 210))
        self.screen.blit(start_hint, (cx - start_hint.get_width()//2, cy + 72))
        self.screen.blit(speed_hint, (cx - speed_hint.get_width()//2, cy + 122))
        self.screen.blit(exit_hint, (cx - exit_hint.get_width()//2, cy + 172))

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

    def get_tower_btn_center(self, idx):
        # Compute same sizing logic as draw_ui so hit detection matches visuals
        tower_count = len(TOWER_TYPES)
        tower_spacing = 132
        total_width = tower_count * tower_spacing
        start_x = SCREEN_W - 80 - total_width + tower_spacing // 2
        cx = start_x + idx * tower_spacing
        cy = ROWS * GRID_SIZE + 106
        return cx, cy, 46

    def menu_button_rects(self):
        # Centered small menu with Resume / Quit
        w = 340
        h = 160
        cx = SCREEN_W // 2
        cy = SCREEN_H // 2
        box = pygame.Rect(cx - w//2, cy - h//2, w, h)
        btn_w = 140
        btn_h = 40
        resume = pygame.Rect(cx - btn_w - 12, cy + 10, btn_w, btn_h)
        quit_b = pygame.Rect(cx + 12, cy + 10, btn_w, btn_h)
        return box, resume, quit_b

    def draw_menu(self):
        box, resume, quit_b = self.menu_button_rects()
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        pygame.draw.rect(self.screen, (36, 32, 28), box, border_radius=12)
        pygame.draw.rect(self.screen, (120, 110, 90), box, 3, border_radius=12)
        title = self.font_big.render("PAUS – Spelet pausat", True, WHITE)
        self.screen.blit(title, (box.x + box.w//2 - title.get_width()//2, box.y + 14))
        # Buttons
        pygame.draw.rect(self.screen, (24, 120, 24), resume, border_radius=8)
        pygame.draw.rect(self.screen, (120, 24, 24), quit_b, border_radius=8)
        rtxt = self.font_med.render("Fortsätt", True, WHITE)
        qtxt = self.font_med.render("Avsluta", True, WHITE)
        self.screen.blit(rtxt, (resume.x + resume.w//2 - rtxt.get_width()//2, resume.y + 8))
        self.screen.blit(qtxt, (quit_b.x + quit_b.w//2 - qtxt.get_width()//2, quit_b.y + 8))

    async def run(self):
        tower_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]
        tower_list = list(TOWER_TYPES.keys())
        running = True
        while running:
            ms = self.clock.tick(60)
            dt = ms / 1000.0
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if self.show_intro:
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            self.show_intro = False
                            self.stop_intro_music()
                            # reset some states to begin
                            self._init_level()
                            self._reset_wave_state()
                            self.play_placement_music()
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit(0)
                        continue

                    if event.key == pygame.K_r:
                        self.full_reset()

                    elif event.key == pygame.K_ESCAPE:
                        # Toggle in-game menu / pause
                        self.show_menu = not self.show_menu
                        self.paused = self.show_menu

                    # Nivå klar → nästa nivå
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.level_complete and self.level < max(LEVEL_WAVES.keys()):
                            self.begin_next_level()
                        elif self.level_transition:
                            self.level_transition = False
                    elif event.key == pygame.K_F11 or event.key == pygame.K_f:
                        self.toggle_fullscreen()

                    # Välj torn med [1-6]
                    for i, k in enumerate(tower_keys):
                        if event.key == k and i < len(tower_list):
                            if self.tower_unlocked(tower_list[i]):
                                self.selected_tower_type = tower_list[i]

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.show_intro:
                        continue
                    # If menu is open, handle menu button clicks
                    if self.show_menu:
                        box, resume, quit_b = self.menu_button_rects()
                        if resume.collidepoint(mx, my):
                            self.show_menu = False
                            self.paused = False
                        elif quit_b.collidepoint(mx, my):
                            pygame.quit()
                            sys.exit(0)
                        continue

                    if self.level_transition:
                        self.level_transition = False
                        continue
                    handled = False
                    for i in range(len(TOWER_TYPES)):
                        cx, cy, radius = self.get_tower_btn_center(i)
                        if (mx - cx) ** 2 + (my - cy) ** 2 <= radius ** 2:
                            ttype = tower_list[i]
                            if self.tower_unlocked(ttype):
                                self.selected_tower_type = ttype
                                # trigger press animation
                                self.ui_state['towers'][ttype]['press'] = 1.0
                                if self.weapon_click_sound:
                                    self.weapon_click_sound.play()
                            handled = True
                            break
                    # Kolla klick på assembly-popup
                    if not handled and self.show_assembly:
                        if self._handle_assembly_click(mx, my):
                            handled = True
                    # Kolla klick på smidesbord-knapp
                    if not handled and self.between_waves and not self.level_complete:
                        abtn = self._assembly_btn_rect()
                        if abtn.collidepoint(mx, my):
                            self.show_assembly = not self.show_assembly
                            handled = True
                    # Kolla klick på vapendel på kartan
                    if not handled and my < ROWS * GRID_SIZE and not self.game_over:
                        for p in list(self.parts_on_map):
                            if p.hit(mx, my):
                                if len(self.collected_parts) < 9:
                                    self.collected_parts.append(p.ptype)
                                    self.parts_on_map.remove(p)
                                handled = True
                                break
                    if not handled:
                        ui_y = ROWS * GRID_SIZE
                        cx_btn = SCREEN_W // 2
                        cy_btn = ui_y + 48
                        radius = 52
                        if ((mx - cx_btn) ** 2 + (my - cy_btn) ** 2 <= radius ** 2) and self.between_waves and self.wave_complete_timer == 0 and not self.level_complete:
                            # press animation
                            self.ui_state['wave_press'] = 1.0
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

            keys = pygame.key.get_pressed()
            if not self.show_intro and keys[pygame.K_SPACE]:
                self.speed_multiplier = 2.0
            else:
                self.speed_multiplier = 1.0

            if not self.show_menu and not self.show_intro:
                self.update(dt)
            if self.show_intro:
                self.draw_intro()
            else:
                if self.level_transition:
                    self.draw_level_transition()
                else:
                    self.draw_map()

                    # Räckviddsförhandsvisning
                    if my < ROWS * GRID_SIZE and not self.level_complete:
                        col, row = px_to_grid(mx, my)
                        if not self.grid_occupied(col, row):
                            px3, py3 = grid_to_px(col, row)
                            tdata     = TOWER_TYPES[self.selected_tower_type]
                            free_here = self.selected_tower_type in self.free_tower_queue
                            unlocked  = self.tower_unlocked(self.selected_tower_type) or free_here
                            pygame.draw.circle(self.screen,
                                               (200,200,200) if unlocked else DARK_GRAY,
                                               (px3 + self.current_shake_x, py3 + self.current_shake_y), tdata["range"], 1)
                            hint_col = tdata["color"] if (
                                (self.money >= tdata["cost"] or free_here) and unlocked) else DARK_GRAY
                            pygame.draw.rect(self.screen, hint_col,
                                             (col*GRID_SIZE+3 + self.current_shake_x, row*GRID_SIZE+3 + self.current_shake_y, GRID_SIZE-6, GRID_SIZE-6), 2)

                    for t in self.towers:
                        t.draw(self.screen, selected=(self.selected_tower == t), shake=(self.current_shake_x, self.current_shake_y))
                    for e in self.effects:
                        e.draw(self.screen, shake=(self.current_shake_x, self.current_shake_y))
                    for b in self.bullets:
                        b.draw(self.screen, shake=(self.current_shake_x, self.current_shake_y))
                    for z in self.zombies:
                        z.draw(self.screen, shake=(self.current_shake_x, self.current_shake_y))
                    # Vapendelar blinkar på kartan
                    self.draw_parts_on_map()

                    self.draw_boss_bar()
                    self.draw_wave_progress()
                    self.draw_ui()
                    for banner in self.banners:
                        banner.draw(self.screen, self.font_big)
                    self.banners = [b for b in self.banners if b.timer > 0]

                    if self.game_over:
                        self.draw_game_over()
                    elif self.level_complete:
                        self.draw_level_complete()
                    # draw scheduled countdown if active
                    self.draw_countdown()
                    # Smidesbord-popup (ovanpå allt annat)
                    self.draw_assembly_ui()
                if self.show_menu:
                    self.draw_menu()

            await asyncio.sleep(0)
            pygame.display.flip()

        pygame.quit()


async def main():
    await Game().run()

if __name__ == "__main__":
    asyncio.run(main())
