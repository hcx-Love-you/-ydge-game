name: Build Web & APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
        
    - name: Install Pygbag
      run: |
        pip install pygbag
        
    - name: Compile Python to WebAssembly
      run: |
        pygbag --build main.py
        
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install Capacitor and build APK
      run: |
        npm init -y
        npm install @capacitor/core @capacitor/cli @capacitor/android
        npx cap init "废土生存" "org.ydge.ydge" --web-dir=build/web
        
        npx cap add android
        npx cap sync android
        
        cd android
        chmod +x gradlew
        ./gradlew assembleDebug
        
    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: ydge-apk
        path: android/app/build/outputs/apk/debug/app-debug.apk
