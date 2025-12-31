import sys
from pathlib import Path
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
    (255, 95, 86),    # đỏ
    (255, 189, 46),   # vàng
    (39, 201, 63)     # xanh
]


# ========= HELPERS =========
def vertical_gradient(size, top_color, bottom_color):
    """Tạo ảnh gradient dọc từ top_color đến bottom_color"""
    w, h = size
    img = Image.new("RGB", size, top_color)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        draw.line((0, y, w, y), fill=(r, g, b))
    return img


def rounded_mask(size, radius):
    """Tạo mask bo góc tròn"""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1),
        radius=radius,
        fill=255
    )
    return mask


# ========= MAIN =========
def carbonize(input_path: str):
    """
    Biến ảnh code thành kiểu Carbon (macOS window + gradient background).
    Lưu kết quả thành file mới với hậu tố _carbon.png
    """
    input_path = Path(input_path)
    if not input_path.is_file():
        print(f"File không tồn tại: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Mở và chuẩn bị ảnh code
    code_img = Image.open(input_path).convert("RGBA")
    iw, ih = code_img.size

    # Bo góc riêng cho ảnh code trước khi dán
    code_mask = rounded_mask((iw, ih), RADIUS)
    code_rounded = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    code_rounded.paste(code_img, (0, 0))
    code_rounded.putalpha(code_mask)

    # Kích thước window
    window_w = iw
    window_h = HEADER_HEIGHT + ih

    # Kích thước canvas
    canvas_w = window_w + CANVAS_MARGIN * 2
    canvas_h = window_h + CANVAS_MARGIN * 2

    # Tạo canvas gradient
    canvas = vertical_gradient(
        (canvas_w, canvas_h),
        BG_TOP, BG_BOTTOM
    ).convert("RGBA")

    # Tạo window layer
    window = vertical_gradient(
        (window_w, window_h),
        WINDOW_TOP, WINDOW_BOTTOM
    ).convert("RGBA")

    draw = ImageDraw.Draw(window)

    # Vẽ 3 nút macOS
    dot_radius = 6
    dot_y = HEADER_HEIGHT // 2
    dot_x = 16  # lề trái hợp lý hơn
    for color in DOT_COLORS:
        draw.ellipse(
            (dot_x - dot_radius, dot_y - dot_radius,
             dot_x + dot_radius, dot_y + dot_radius),
            fill=color
        )
        dot_x += 24  # khoảng cách giữa các nút

    # Dán ảnh code đã bo góc vào window
    window.paste(
        code_rounded,
        (0, HEADER_HEIGHT),
        code_rounded
    )

    # Bo góc toàn bộ window
    window_mask = rounded_mask(window.size, RADIUS)

    # Căn giữa window trên canvas
    wx = (canvas_w - window_w) // 2
    wy = (canvas_h - window_h) // 2

    canvas.paste(window, (wx, wy), window_mask)

    # Lưu file mới
    output_path = input_path.with_stem(input_path.stem + "_carbon").with_suffix(".png")
    canvas.save(output_path)
    print(f"Đã lưu: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Cách dùng: python carbonize.py <đường_dẫn_ảnh>")
        sys.exit(1)

    try:
        carbonize(sys.argv[1])
    except Exception as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        sys.exit(1)