[app]

# 你的游戏名称
title = 废土生存

# 包名 (必须是纯英文，不能有数字和连字符，且必须是三段式)
package.name = wastelandsurvival
package.domain = org.test

# 源码目录
source.dir = .

# 包含的文件后缀 (如果你有图片、json文件，一定要加在这里)
source.include_exts = py,png,jpg,kv,atlas,json,txt

# 游戏版本
version = 0.1

# 🔥 核心修复：锁定 Python 3.11.9 和 Cython 0.29.36，避免最新版导致编译崩溃
requirements = python3==3.11.9,hostpython3==3.11.9,cython==0.29.36,pygame-ce,kivy==2.3.0

# 屏幕方向 (landscape 横屏, portrait 竖屏)
orientation = landscape

# 是否全屏
fullscreen = 1

# 安卓 API 版本
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# 允许在后台推演
android.wakelock = True
