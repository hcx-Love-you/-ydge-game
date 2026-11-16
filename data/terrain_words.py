# 地形词库：降低颜色方差，让同类地形看起来是一整片
TERRAIN_TYPES = {
    "深海": {"base_color": (15, 45, 90), "var_range": (2, 5, 8)},
    "海洋": {"base_color": (35, 100, 180), "var_range": (5, 10, 15)},
    "沙滩": {"base_color": (220, 205, 150), "var_range": (5, 5, 5)},
    "平原": {"base_color": (95, 160, 85), "var_range": (5, 8, 5)},
    "森林": {"base_color": (45, 115, 50), "var_range": (5, 10, 5)},
    "沙漠": {"base_color": (215, 195, 120), "var_range": (5, 5, 5)},
    "高山": {"base_color": (130, 130, 130), "var_range": (8, 8, 8)}
}
