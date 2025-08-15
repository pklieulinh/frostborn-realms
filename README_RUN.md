# Python Prototype (Pixi.js to Pygame Transition)

## Mục tiêu
Tạo bản prototype Python tương đương tối thiểu để kiểm chứng:
- Pipeline Asset Manifest
- ECS đơn giản
- Game loop, rendering, animation strip cơ bản
- Khả năng mở rộng sang animation/state machine

## Cài đặt
```
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

## Chạy
```
python main.py
```

## Thêm Asset
Đặt PNG vào:
```
assets/images/tilesets/
assets/images/characters/
assets/images/icons/
assets/images/fx/
assets/images/ui/
```
Cập nhật `assets/asset-manifest.json` rồi chạy lại game.

## Animation
Nếu ảnh `chars_settlers` là strip ngang:
- width = frameWidth * frameCount
- Khai báo frameWidth, frameHeight trong manifest.
Engine tự động cắt theo cột.

## Mở rộng Đề xuất
1. State machine nhân vật
2. Hệ thống AnimationEvent
3. Spatial partition
4. Hot reload manifest (watch mtime)
5. Atlas builder (Python PIL)
6. Network sync (websocket)

## Export Web
Khảo sát: pygbag hoặc transpile (giảm hiệu năng). Tạm thời native desktop.
