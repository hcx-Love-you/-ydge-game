[app]

title = 废土生存
package.name = wastelandsurvival
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt
version = 0.1

# 锁定兼容版本
requirements = python3==3.11.9,hostpython3==3.11.9,cython==0.29.36,pygame-ce,kivy==2.3.0

# 🔥 核心修复：强制 Buildozer 自动接受 Android SDK 许可
android.accept_sdk_license = True

orientation = landscape
fullscreen = 1
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.wakelock = True
