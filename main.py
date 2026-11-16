# 这是一个使用 Kivy 框架的废土生存单机测试版
import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import random

# 强制横屏
Window.fullscreen = 'auto'

class WastelandGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = 20
        self.spacing = 20
        
        # 左侧控制台
        left_panel = BoxLayout(orientation='vertical', size_hint=(0.3, 1), spacing=10)
        
        self.coord_label = Label(text="坐标: 0, 0\n地形: 平原", font_size='24sp', halign='center')
        left_panel.add_widget(self.coord_label)
        
        # 按钮区
        btn_layout = GridLayout(cols=1, spacing=10, size_hint=(1, 0.6))
        self.btn_up = Button(text="↑ 向上探索", font_size='20sp', background_color=(0.2, 0.6, 0.8, 1))
        self.btn_down = Button(text="↓ 向下探索", font_size='20sp', background_color=(0.2, 0.6, 0.8, 1))
        self.btn_left = Button(text="← 向左探索", font_size='20sp', background_color=(0.2, 0.6, 0.8, 1))
        self.btn_right = Button(text="→ 向右探索", font_size='20sp', background_color=(0.2, 0.6, 0.8, 1))
        
        self.btn_up.bind(on_press=lambda x: self.move(0, 1))
        self.btn_down.bind(on_press=lambda x: self.move(0, -1))
        self.btn_left.bind(on_press=lambda x: self.move(-1, 0))
        self.btn_right.bind(on_press=lambda x: self.move(1, 0))
        
        btn_layout.add_widget(self.btn_up)
        btn_layout.add_widget(self.btn_down)
        btn_layout.add_widget(self.btn_left)
        btn_layout.add_widget(self.btn_right)
        
        left_panel.add_widget(btn_layout)
        
        # 右侧主界面
        right_panel = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
        self.main_label = Label(text="欢迎来到废土世界\n点击左侧按钮移动", font_size='32sp')
        right_panel.add_widget(self.main_label)
        
        self.add_widget(left_panel)
        self.add_widget(right_panel)
        
        self.x, self.y = 0, 0
        self.terrains = ["平原", "森林", "沙漠", "高山", "海洋"]

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        # 根据坐标随机生成地形（模拟单机逻辑）
        random.seed((self.x * 73856093) ^ (self.y * 19349663))
        terrain = random.choice(self.terrains)
        
        self.coord_label.text = f"坐标: {self.x}, {self.y}\n地形: {terrain}"
        self.main_label.text = f"你来到了 ({self.x}, {self.y})\n这里是一片{terrain}。"

class WastelandApp(App):
    def build(self):
        self.title = "废土生存 - 单机测试版"
        return WastelandGame()

if __name__ == '__main__':
    WastelandApp().run()
