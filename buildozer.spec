[app]
title = 废土生存
package.name = ydge
package.domain = org.ydge
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,otf,json
version = 0.1
requirements = python3,kivy==2.3.0
orientation = landscape
fullscreen = 1
android.accept_sdk_license = True
android.api = 31
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
android.cflags = -Wno-error=format-security

[buildozer]
log_level = 2
warn_on_root = 1
p4a.branch = develop
# 核心：限制 Gradle 打包时的 Java 内存，防止最后阶段爆掉
gradle.parameters = org.gradle.jvmargs=-Xmx2048m -Dorg.gradle.daemon=false
