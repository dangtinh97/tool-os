import sys
from PIL import Image, ImageDraw

# ========= CONFIG =========
HEADER_HEIGHT = 56
RADIUS = 22
CANVAS_MARGIN = 40

# Nền ngoài
BG_TOP = (190, 198, 202)
BG_BOTTOM = (160, 168, 172)

# Nền window
WINDOW_TOP = (26, 29, 30)
WINDOW_BOTTOM = (18, 20, 21)

# MacOS dots
DOT_COLORS = [
    (255, 95, 86),
    (255, 189, 46),
    (39, 201, 63)
]


# ========= HELPERS =========
def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        draw.line((0, y, w, y), fill=(r, g, b))
    return img


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1),  # -1 để bo góc chính xác hơn
        radius=radius,
        fill=255
    )
    return mask


# ========= MAIN =========
def carbonize(image_path):
    code_img = Image.open(image_path).convert("RGBA")
    iw, ih = code_img.size

    # ===== BO GÓC RIÊNG CHO ẢNH CODE =====
    # Tạo mask bo góc chỉ cho phần ảnh code (không có header)
    code_mask = rounded_mask((iw, ih), RADIUS)

    # Áp mask bo góc lên ảnh code gốc
    code_rounded = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    code_rounded.paste(code_img, (0, 0), code_img)  # dán gốc trước
    code_rounded.paste(code_img, (0, 0), code_mask)  # áp mask để bo góc

    # Window size: header + ảnh code full bleed
    window_w = iw
    window_h = HEADER_HEIGHT + ih

    # Canvas
    canvas_w = window_w + CANVAS_MARGIN * 2
    canvas_h = window_h + CANVAS_MARGIN * 2

    canvas = vertical_gradient(
        (canvas_w, canvas_h),
        BG_TOP, BG_BOTTOM
    ).convert("RGBA")

    # Window layer
    window = vertical_gradient(
        (window_w, window_h),
        WINDOW_TOP, WINDOW_BOTTOM
    ).convert("RGBA")

    draw = ImageDraw.Draw(window)

    # Vẽ 3 nút MacOS
    dot_x = 28
    dot_y = HEADER_HEIGHT // 2
    for color in DOT_COLORS:
        draw.ellipse(
            (dot_x - 6, dot_y - 6, dot_x + 6, dot_y + 6),
            fill=color
        )
        dot_x += 20

    # Dán ảnh code ĐÃ BO GÓC vào vị trí dưới header
    window.paste(
        code_rounded,
        (0, HEADER_HEIGHT),
        code_rounded  # vẫn dùng alpha
    )

    # Bo góc toàn bộ window (header + ảnh code đã bo)
    mask = rounded_mask(window.size, RADIUS)

    # Căn giữa window trên canvas
    wx = (canvas_w - window_w) // 2
    wy = (canvas_h - window_h) // 2

    canvas.paste(window, (wx, wy), mask)

    # === GỢI Ý: Không lưu đè file gốc nữa ===
    # output_path = image_path.replace(".png", "_carbon.png")
    # canvas.save(output_path)

    canvas.save(image_path)  # tạm giữ nguyên như cũ


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    try:
        carbonize(sys.argv[1])
    except Exception as e:
        with open("C:/tools/carbon_error.log", "a", encoding="utf-8") as f:
            f.write(str(e) + "\n")
