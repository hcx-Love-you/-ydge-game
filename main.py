from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

Window.fullscreen = 'auto'

class GameRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=50, **kwargs)
        
        self.x_coord = 0
        self.y_coord = 0
        
        self.label = Label(text="废土坐标: 0, 0\n状态: 单机离线运行", font_size='30sp', halign='center')
        self.add_widget(self.label)
        
        btn = Button(text="向右移动一格", font_size='24sp', size_hint=(1, 0.3))
        btn.bind(on_press=self.move_right)
        self.add_widget(btn)

    def move_right(self, instance):
        self.x_coord += 1
        self.label.text = f"废土坐标: {self.x_coord}, {self.y_coord}\n状态: 单机离线运行"

class WastelandApp(App):
    def build(self):
        self.title = "废土生存 - 纯单机测试"
        return GameRoot()

if __name__ == '__main__':
    WastelandApp().run()
