import pygame
import sys
import os
import math
import random
import asyncio

sys.path.append(os.getcwd())
try:
    from data import terrain_words
except ImportError:
    print("警告：未找到 data.terrain_words 模块")

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
CHUNK_SCALE = 50
VIEW_RANGE = 5

COLOR_BG = (15, 18, 25)
COLOR_PANEL_BG = (25, 30, 40)
COLOR_BORDER = (0, 255, 200)
COLOR_TEXT = (200, 200, 200)
COLOR_BTN = (40, 50, 70)

GAME_STATE = {"coord": (0, 0), "show_menu": False}

class TerrainEngine:
    def __init__(self):
        self.cache = {}

    def get_info(self, x, y):
        key = f"{x},{y}"
        if key in self.cache: return self.cache[key]

        v1 = math.sin(x * 0.03) + math.cos(y * 0.03)
        v2 = math.sin(x * 0.1 + 1.5) + math.cos(y * 0.1 + 1.5)
        v3 = math.sin(x * 0.4 + 3.0) + math.cos(y * 0.4 + 3.0)
        elevation = (v1 + v2 * 0.5 + v3 * 0.25 + 4.0) / 8.0 
        moisture = (math.cos(x * 0.05 + 2.0) + math.sin(y * 0.05 + 2.0) + 2.0) / 4.0

        if elevation < 0.3: terrain = "深海"
        elif elevation < 0.4: terrain = "海洋"
        elif elevation < 0.45: terrain = "沙滩"
        elif elevation > 0.8: terrain = "高山"
        elif moisture > 0.6: terrain = "森林"
        elif moisture < 0.3: terrain = "沙漠"
        else: terrain = "平原"

        t_data = terrain_words.TERRAIN_TYPES.get(terrain, {"base_color": (50,50,50), "var_range": (0,0,0)})
        rng = random.Random((x * 73856093) ^ (y * 19349663))
        base_r, base_g, base_b = t_data["base_color"]
        var_r, var_g, var_b = t_data["var_range"]

        color = (
            max(0, min(255, base_r + rng.randint(-var_r, var_r))),
            max(0, min(255, base_g + rng.randint(-var_g, var_g))),
            max(0, min(255, base_b + rng.randint(-var_b, var_b)))
        )

        resource = None
        is_big_tree = False
        is_blocked = False
        tree_type = None

        if terrain == "深海": is_blocked = True
        if terrain == "森林":
            if rng.random() > 0.8:
                is_big_tree = True
                is_blocked = True
                tree_type = "阔叶树" if moisture > 0.7 else "针叶树"
                resource = tree_type
            elif rng.random() > 0.4: resource = "灌木丛"
            else: resource = "杂草"
        elif terrain == "高山" and rng.random() > 0.7:
            is_big_tree = True; is_blocked = True; tree_type = "寒带松"; resource = tree_type
        elif terrain == "沙滩" and rng.random() > 0.6:
            is_big_tree = True; is_blocked = True; tree_type = "椰子树"; resource = tree_type
        elif terrain == "平原" and rng.random() > 0.8: resource = "野花"
        elif terrain == "沙漠":
            roll = rng.random()
            if roll > 0.88:
                is_big_tree = True; is_blocked = True; tree_type = "巨型仙人掌"; resource = tree_type
            elif roll > 0.70: resource = "小仙人掌"

        self.cache[key] = {"terrain": terrain, "color": color, "resource": resource, "is_big_tree": is_big_tree, "is_blocked": is_blocked, "tree_type": tree_type}
        return self.cache[key]

engine = TerrainEngine()

class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.virtual_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("废土生存 - 触屏长按/键盘双模版")
        
        font_path = "/system/fonts/NotoSansCJK-Regular.ttc"
        self.font = pygame.font.Font(font_path, 22) if os.path.exists(font_path) else pygame.font.SysFont("arial", 22)
        self.title_font = pygame.font.Font(font_path, 36) if os.path.exists(font_path) else pygame.font.SysFont("arial", 36)
        self.small_font = pygame.font.Font(font_path, 18) if os.path.exists(font_path) else pygame.font.SysFont("arial", 18)

        self.move_timer = 0
        self.move_cooldown = 12
        self.keys_state = {"up": False, "down": False, "left": False, "right": False}
        self.touch_state = {"up": False, "down": False, "left": False, "right": False}

    def move_player(self, dx, dy):
        cx, cy = GAME_STATE["coord"]
        target_x, target_y = cx + dx, cy + dy
        target_info = engine.get_info(target_x, target_y)
        if target_info["is_blocked"]: return False
        GAME_STATE["coord"] = (target_x, target_y)
        return True

    def draw_center_scene(self, x, y, w, h):
        pygame.draw.rect(self.virtual_screen, (20, 20, 20), (x, y, w, h), border_radius=10)
        pygame.draw.rect(self.virtual_screen, COLOR_BORDER, (x, y, w, h), 2, border_radius=10)

        cx, cy = GAME_STATE["coord"]
        tile_size = min(w, h) // (VIEW_RANGE * 2 + 1)
        center_x, center_y = x + w // 2, y + h // 2
        current_info = engine.get_info(cx, cy)
        
        res_text = f" | 资源: {current_info['resource']}" if current_info['resource'] else ""
        self.virtual_screen.blit(self.title_font.render(f"{current_info['terrain']}{res_text}", True, COLOR_TEXT), (x + 20, y + 10))

        for i in range(-VIEW_RANGE, VIEW_RANGE + 1):
            for j in range(-VIEW_RANGE, VIEW_RANGE + 1):
                tx, ty = cx + i, cy + j
                info = engine.get_info(tx, ty)
                rect_x = center_x + i * tile_size - tile_size // 2
                rect_y = center_y + j * tile_size - tile_size // 2

                pygame.draw.rect(self.virtual_screen, info["color"], (rect_x, rect_y, tile_size, tile_size))
                border_color = (max(0, info["color"][0]-15), max(0, info["color"][1]-15), max(0, info["color"][2]-15))
                pygame.draw.rect(self.virtual_screen, border_color, (rect_x, rect_y, tile_size, tile_size), 1)

                if not info["is_big_tree"] and info["resource"]:
                    px, py = rect_x + tile_size//2, rect_y + tile_size//2
                    rng = random.Random((tx * 73856093) ^ (ty * 19349663))
                    if info["resource"] == "灌木丛":
                        for _ in range(3):
                            gx = rect_x + rng.randint(10, tile_size-10)
                            gy = rect_y + rng.randint(10, tile_size-10)
                            pygame.draw.circle(self.virtual_screen, (30, 80, 40), (gx, gy), 6)
                            pygame.draw.circle(self.virtual_screen, (40, 100, 50), (gx-2, gy-2), 4)
                    elif info["resource"] == "杂草":
                        pygame.draw.line(self.virtual_screen, (60, 130, 60), (px, py+5), (px-4, py-6), 2)
                        pygame.draw.line(self.virtual_screen, (60, 130, 60), (px, py+5), (px+4, py-6), 2)
                    elif info["resource"] == "野花":
                        pygame.draw.circle(self.virtual_screen, (255, 200, 200), (px, py), 4)
                    elif info["resource"] == "小仙人掌":
                        pygame.draw.rect(self.virtual_screen, (60, 140, 60), (px - 4, py - 10, 8, 15), border_radius=2)
                        pygame.draw.rect(self.virtual_screen, (30, 80, 30), (px - 4, py - 10, 8, 15), 1, border_radius=2)
                        pygame.draw.rect(self.virtual_screen, (60, 140, 60), (px - 10, py - 5, 6, 4))
                        pygame.draw.rect(self.virtual_screen, (60, 140, 60), (px + 4, py - 8, 6, 4))

        entities = [{"type": "player", "x": center_x, "y": center_y, "z": cy}]
        for i in range(-VIEW_RANGE, VIEW_RANGE + 1):
            for j in range(-VIEW_RANGE, VIEW_RANGE + 1):
                tx, ty = cx + i, cy + j
                info = engine.get_info(tx, ty)
                if info["is_big_tree"]:
                    rect_x = center_x + i * tile_size
                    rect_y = center_y + j * tile_size
                    entities.append({"type": "big_tree", "x": rect_x, "y": rect_y, "z": ty, "tx": tx, "ty": ty, "tree_type": info["tree_type"]})

        entities.sort(key=lambda e: e["z"])

        for ent in entities:
            if ent["type"] == "big_tree":
                t_rect_x, t_rect_y, t_type = ent["x"], ent["y"], ent["tree_type"]
                if t_type in ["针叶树", "寒带松"]:
                    trunk_rect = pygame.Rect(t_rect_x - tile_size*0.15, t_rect_y - tile_size*0.5, tile_size*0.3, tile_size*0.8)
                    pygame.draw.rect(self.virtual_screen, (60, 40, 20), trunk_rect)
                    pygame.draw.rect(self.virtual_screen, (20, 20, 20), trunk_rect, 2)
                    canopy1 = [(t_rect_x, t_rect_y - tile_size*1.8), (t_rect_x - tile_size*0.6, t_rect_y - tile_size*0.5), (t_rect_x + tile_size*0.6, t_rect_y - tile_size*0.5)]
                    pygame.draw.polygon(self.virtual_screen, (25, 80, 35), canopy1)
                    pygame.draw.polygon(self.virtual_screen, (10, 30, 10), canopy1, 2)
                    canopy2 = [(t_rect_x, t_rect_y - tile_size*2.4), (t_rect_x - tile_size*0.4, t_rect_y - tile_size*1.2), (t_rect_x + tile_size*0.4, t_rect_y - tile_size*1.2)]
                    pygame.draw.polygon(self.virtual_screen, (35, 110, 50), canopy2)
                    pygame.draw.polygon(self.virtual_screen, (10, 30, 10), canopy2, 2)
                elif t_type == "阔叶树":
                    trunk_rect = pygame.Rect(t_rect_x - tile_size*0.15, t_rect_y - tile_size*0.4, tile_size*0.3, tile_size*0.7)
                    pygame.draw.rect(self.virtual_screen, (80, 50, 30), trunk_rect)
                    pygame.draw.rect(self.virtual_screen, (20, 20, 20), trunk_rect, 2)
                    center_node = (t_rect_x, t_rect_y - tile_size*1.2)
                    pygame.draw.circle(self.virtual_screen, (40, 100, 50), center_node, int(tile_size*0.7))
                    pygame.draw.circle(self.virtual_screen, (20, 50, 20), center_node, int(tile_size*0.7), 2)
                elif t_type == "椰子树":
                    pygame.draw.lines(self.virtual_screen, (120, 80, 40), False, [(t_rect_x, t_rect_y + tile_size*0.3), (t_rect_x - tile_size*0.1, t_rect_y - tile_size*0.5), (t_rect_x, t_rect_y - tile_size*1.2)], 4)
                    for angle in [-0.5, 0.5, -1.2, 1.2, 0]:
                        leaf_end_x = t_rect_x + math.sin(angle) * tile_size * 0.8
                        leaf_end_y = t_rect_y - tile_size*1.2 + math.cos(angle) * tile_size * 0.4
                        pygame.draw.line(self.virtual_screen, (30, 100, 40), (t_rect_x, t_rect_y - tile_size*1.2), (leaf_end_x, leaf_end_y), 4)
                elif t_type == "巨型仙人掌":
                    c_green, c_dark = (60, 150, 60), (30, 80, 30)
                    line_w = max(6, int(tile_size * 0.2)); outline_w = line_w + 4
                    base_x, base_y = t_rect_x, t_rect_y + tile_size*0.2
                    top_x, top_y = t_rect_x, t_rect_y - tile_size*1.4
                    pygame.draw.line(self.virtual_screen, c_dark, (base_x, base_y), (top_x, top_y), outline_w)
                    pygame.draw.line(self.virtual_screen, c_green, (base_x, base_y), (top_x, top_y), line_w)
                    pygame.draw.circle(self.virtual_screen, c_dark, (top_x, top_y), outline_w // 2)
                    pygame.draw.circle(self.virtual_screen, c_green, (top_x, top_y), line_w // 2)

            elif ent["type"] == "player":
                px, py = ent["x"], ent["y"]
                player_w = tile_size * 0.4
                player_h = tile_size * 0.5
                pygame.draw.ellipse(self.virtual_screen, (0, 0, 0), (px - player_w//2, py + player_h//2 - 5, player_w, 10))
                pygame.draw.rect(self.virtual_screen, (60, 60, 80), (px - player_w//2, py, player_w, player_h), border_radius=5)
                head_r = player_w * 0.6
                pygame.draw.circle(self.virtual_screen, (255, 240, 220), (px, py - head_r*0.5), head_r)
                pygame.draw.polygon(self.virtual_screen, (192, 192, 192), [(px - head_r, py - head_r*1.2), (px - head_r*0.5, py - head_r*2), (px, py - head_r*1.5), (px + head_r*0.5, py - head_r*2), (px + head_r, py - head_r*1.2)])
                pygame.draw.circle(self.virtual_screen, (0, 100, 255), (px - head_r*0.3, py - head_r*0.5), max(1, int(head_r*0.15)))
                pygame.draw.circle(self.virtual_screen, (0, 100, 255), (px + head_r*0.3, py - head_r*0.5), max(1, int(head_r*0.15)))

    def draw_mini_map(self, x, y):
        cx, cy = GAME_STATE["coord"]
        mx, my = cx // CHUNK_SCALE, cy // CHUNK_SCALE
        local_x, local_y = cx % CHUNK_SCALE, cy % CHUNK_SCALE
        tile_size, gap = 26, 2
        for i in range(-2, 3):
            for j in range(-2, 3):
                t_mx, t_my = mx + i, my + j
                info = engine.get_info(t_mx * CHUNK_SCALE + CHUNK_SCALE//2, t_my * CHUNK_SCALE + CHUNK_SCALE//2)
                rect_x = x + (i + 2) * (tile_size + gap)
                rect_y = y + (j + 2) * (tile_size + gap)
                pygame.draw.rect(self.virtual_screen, info["color"], (rect_x, rect_y, tile_size, tile_size), border_radius=2)
                if i == 0 and j == 0:
                    pygame.draw.rect(self.virtual_screen, (255, 50, 50), (rect_x, rect_y, tile_size, tile_size), 2, border_radius=2)
                    px = rect_x + (local_x / CHUNK_SCALE) * tile_size
                    py = rect_y + (local_y / CHUNK_SCALE) * tile_size
                    pygame.draw.circle(self.virtual_screen, (255, 255, 255), (int(px), int(py)), 4)

    def draw_game_scene(self):
        self.virtual_screen.fill(COLOR_BG)
        
        # 【新增】左上角控制台/模组按钮
        btn_rect = pygame.Rect(20, 20, 120, 40)
        pygame.draw.rect(self.virtual_screen, COLOR_BTN, btn_rect, border_radius=5)
        pygame.draw.rect(self.virtual_screen, COLOR_BORDER, btn_rect, 2, border_radius=5)
        btn_text = self.font.render("⚙ 控制台", True, COLOR_TEXT)
        self.virtual_screen.blit(btn_text, (btn_rect.x + 10, btn_rect.y + 8))

        pygame.draw.rect(self.virtual_screen, COLOR_PANEL_BG, (20, 70, 300, SCREEN_HEIGHT - 90), border_radius=10)
        pygame.draw.rect(self.virtual_screen, COLOR_BORDER, (20, 70, 300, SCREEN_HEIGHT - 90), 2, border_radius=10)
        self.virtual_screen.blit(self.title_font.render("控制台", True, COLOR_TEXT), (40, 80))

        cx, cy = GAME_STATE["coord"]
        self.virtual_screen.blit(self.font.render(f"坐标: {cx}, {cy}", True, (100, 200, 255)), (40, 130))
        self.virtual_screen.blit(self.small_font.render("区域雷达 (宏观)", True, COLOR_TEXT), (40, 180))
        self.draw_mini_map(40, 210)

        # 触屏方向盘
        pygame.draw.rect(self.virtual_screen, COLOR_BTN, (130, 550, 60, 60), border_radius=8)
        self.virtual_screen.blit(self.title_font.render("↑", True, COLOR_TEXT), (145, 555))
        pygame.draw.rect(self.virtual_screen, COLOR_BTN, (130, 620, 60, 60), border_radius=8)
        self.virtual_screen.blit(self.title_font.render("↓", True, COLOR_TEXT), (145, 625))
        pygame.draw.rect(self.virtual_screen, COLOR_BTN, (60, 620, 60, 60), border_radius=8)
        self.virtual_screen.blit(self.title_font.render("←", True, COLOR_TEXT), (75, 625))
        pygame.draw.rect(self.virtual_screen, COLOR_BTN, (200, 620, 60, 60), border_radius=8)
        self.virtual_screen.blit(self.title_font.render("→", True, COLOR_TEXT), (215, 625))

        self.draw_center_scene(340, 20, 920, 680)

        # 【新增】如果菜单开启，绘制遮罩和模组/修改选项
        if GAME_STATE["show_menu"]:
            # 半透明遮罩
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.virtual_screen.blit(overlay, (0, 0))
            
            # 菜单面板
            menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
            pygame.draw.rect(self.virtual_screen, COLOR_PANEL_BG, menu_rect, border_radius=15)
            pygame.draw.rect(self.virtual_screen, COLOR_BORDER, menu_rect, 2, border_radius=15)
            
            title = self.title_font.render("开发者控制台", True, COLOR_TEXT)
            self.virtual_screen.blit(title, (menu_rect.x + 110, menu_rect.y + 20))
            
            opt1 = self.font.render("1. 加载模组 (Mods)", True, (100, 200, 255))
            opt2 = self.font.render("2. 修改主代码 (需重编译)", True, (100, 200, 255))
            close_btn = self.font.render("❌ 关闭", True, (255, 100, 100))
            
            self.virtual_screen.blit(opt1, (menu_rect.x + 50, menu_rect.y + 100))
            self.virtual_screen.blit(opt2, (menu_rect.x + 50, menu_rect.y + 160))
            self.virtual_screen.blit(close_btn, (menu_rect.x + 280, menu_rect.y + 240))

async def loading_screen(screen, font):
    loading_steps = [
        "正在连接废土网络...",
        "初始化时间引擎（Time Engine）...",
        "正在生成 242 个国家的势力分布...",
        "正在融合 NPC 变异 DNA 词库...",
        "正在演算历史时间线...",
        "世界生成完毕，准备进入！"
    ]
    for i, step in enumerate(loading_steps):
        screen.fill((15, 18, 25)) 
        text_surf = font.render(step, True, (0, 255, 200))
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(text_surf, text_rect)
        
        progress = (i + 1) / len(loading_steps)
        bar_width, bar_height = 400, 20
        bar_x, bar_y = (SCREEN_WIDTH - bar_width) // 2, (SCREEN_HEIGHT - bar_height) // 2 + 50
        pygame.draw.rect(screen, (40, 50, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=10)
        pygame.draw.rect(screen, (0, 255, 200), (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=10)
        
        pygame.display.flip()
        await asyncio.sleep(0.5) 

async def main():
    app = GameApp()
    font_path = "/system/fonts/NotoSansCJK-Regular.ttc"
    loading_font = pygame.font.Font(font_path, 36) if os.path.exists(font_path) else pygame.font.SysFont("arial", 36)
    await loading_screen(app.virtual_screen, loading_font)

    app.running = True
    while app.running:
        await asyncio.sleep(1 / 60) 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                vx, vy = event.pos
                
                # 点击左上角控制台按钮
                if 20 <= vx <= 140 and 20 <= vy <= 60:
                    GAME_STATE["show_menu"] = not GAME_STATE["show_menu"]
                # 如果菜单开着，处理菜单的点击
                elif GAME_STATE["show_menu"]:
                    # 点击关闭按钮
                    if 680 <= vx <= 760 and 410 <= vy <= 450:
                        GAME_STATE["show_menu"] = False
                # 如果没开菜单，处理方向键
                elif not GAME_STATE["show_menu"]:
                    if 130 <= vx <= 190 and 550 <= vy <= 610: app.touch_state["up"] = True
                    elif 130 <= vx <= 190 and 620 <= vy <= 680: app.touch_state["down"] = True
                    elif 60 <= vx <= 120 and 620 <= vy <= 680: app.touch_state["left"] = True
                    elif 200 <= vx <= 260 and 620 <= vy <= 680: app.touch_state["right"] = True
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                app.touch_state = {"up": False, "down": False, "left": False, "right": False}
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]: app.keys_state["up"] = True
                elif event.key in [pygame.K_DOWN, pygame.K_s]: app.keys_state["down"] = True
                elif event.key in [pygame.K_LEFT, pygame.K_a]: app.keys_state["left"] = True
                elif event.key in [pygame.K_RIGHT, pygame.K_d]: app.keys_state["right"] = True
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_w]: app.keys_state["up"] = False
                elif event.key in [pygame.K_DOWN, pygame.K_s]: app.keys_state["down"] = False
                elif event.key in [pygame.K_LEFT, pygame.K_a]: app.keys_state["left"] = False
                elif event.key in [pygame.K_RIGHT, pygame.K_d]: app.keys_state["right"] = False

        if not GAME_STATE["show_menu"]:
            if app.move_timer > 0:
                app.move_timer -= 1
            else:
                moved = False
                if app.keys_state["up"] or app.touch_state["up"]: moved = app.move_player(0, -1)
                elif app.keys_state["down"] or app.touch_state["down"]: moved = app.move_player(0, 1)
                elif app.keys_state["left"] or app.touch_state["left"]: moved = app.move_player(-1, 0)
                elif app.keys_state["right"] or app.touch_state["right"]: moved = app.move_player(1, 0)

                if moved: app.move_timer = app.move_cooldown
                elif any(app.keys_state.values()) or any(app.touch_state.values()): app.move_timer = 5

        app.draw_game_scene()
        app.screen.fill((0, 0, 0))
        app.screen.blit(app.virtual_screen, (0, 0))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
