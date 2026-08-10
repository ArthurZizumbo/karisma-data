"""Compose the competitor evidence figures for Activity 3 from the raw
Playwright captures taken on 9 August 2026.

Produces two figures:
  a3_evidencia_sitios.png  - 2x2 grid of the vendor home pages
  a3_evidencia_precios.png - vendor-published pricing, cropped to be legible
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FIGURAS = Path(__file__).parent / "figuras"

NAVY = (31, 77, 120)
LINE = (203, 213, 225)
MUTED = (100, 116, 139)
WHITE = (255, 255, 255)

MARGIN = 26
GAP = 22
LABEL_H = 46


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Return a sans-serif face, falling back to the PIL default."""
    candidates = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
        if bold
        else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def cell(source: Path, width: int, crop: tuple[int, int, int, int] | None = None) -> Image.Image:
    """Load a capture, optionally crop it, and scale it to the target width."""
    img = Image.open(source).convert("RGB")
    if crop:
        img = img.crop(crop)
    height = round(img.height * width / img.width)
    return img.resize((width, height), Image.LANCZOS)


def grid(items, columns: int, cell_width: int, title: str, out: Path) -> None:
    """Lay out labelled captures on a white canvas and save the result."""
    font_label = load_font(26, bold=True)
    font_title = load_font(32, bold=True)
    font_note = load_font(21)

    tiles = [(label, cell(path, cell_width, crop)) for label, path, crop in items]
    rows = (len(tiles) + columns - 1) // columns
    row_heights = [
        max(t.height for _, t in tiles[r * columns:(r + 1) * columns]) for r in range(rows)
    ]

    width = MARGIN * 2 + columns * cell_width + (columns - 1) * GAP
    height = (
        MARGIN + 54 + sum(h + LABEL_H for h in row_heights) + GAP * (rows - 1) + MARGIN + 34
    )

    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, MARGIN - 8), title, font=font_title, fill=NAVY)

    y = MARGIN + 54
    for r in range(rows):
        x = MARGIN
        for label, tile in tiles[r * columns:(r + 1) * columns]:
            draw.text((x, y + 8), label, font=font_label, fill=NAVY)
            top = y + LABEL_H
            canvas.paste(tile, (x, top))
            draw.rectangle([x, top, x + tile.width - 1, top + tile.height - 1], outline=LINE, width=2)
            x += cell_width + GAP
        y += row_heights[r] + LABEL_H + GAP

    draw.text(
        (MARGIN, height - MARGIN - 20),
        "Capturas tomadas el 9 de agosto de 2026 de las paginas publicas de cada fabricante.",
        font=font_note,
        fill=MUTED,
    )
    canvas.save(out, dpi=(300, 300))
    print(f"{out.name}: {canvas.size}")


grid(
    items=[
        ("Bloomberg Professional Services", FIGURAS / "comp_bloomberg.png", None),
        ("Pyramid Analytics", FIGURAS / "comp_pyramid.png", None),
        ("ThoughtSpot", FIGURAS / "comp_thoughtspot.png", None),
        ("Collibra", FIGURAS / "comp_collibra.png", None),
    ],
    columns=2,
    cell_width=940,
    title="Sitios de los competidores consultados",
    out=FIGURAS / "a3_evidencia_sitios.png",
)

def row_same_height(items, cell_height: int, title: str, out: Path) -> None:
    """Lay captures side by side normalised to a common height.

    Cropping two vendor pages to the same width leaves a large void when their
    aspect ratios differ, so the price figure aligns on height instead.
    """
    font_label = load_font(26, bold=True)
    font_title = load_font(32, bold=True)
    font_note = load_font(21)

    tiles = []
    for label, path, crop in items:
        img = Image.open(path).convert("RGB")
        if crop:
            img = img.crop(crop)
        width = round(img.width * cell_height / img.height)
        tiles.append((label, img.resize((width, cell_height), Image.LANCZOS)))

    width = MARGIN * 2 + sum(t.width for _, t in tiles) + GAP * (len(tiles) - 1)
    height = MARGIN + 54 + LABEL_H + cell_height + MARGIN + 34

    canvas = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, MARGIN - 8), title, font=font_title, fill=NAVY)

    x = MARGIN
    top = MARGIN + 54 + LABEL_H
    for label, tile in tiles:
        draw.text((x, MARGIN + 62), label, font=font_label, fill=NAVY)
        canvas.paste(tile, (x, top))
        draw.rectangle([x, top, x + tile.width - 1, top + tile.height - 1], outline=LINE, width=2)
        x += tile.width + GAP

    draw.text(
        (MARGIN, height - MARGIN - 20),
        "Capturas tomadas el 9 de agosto de 2026 de las paginas publicas de precios de cada fabricante.",
        font=font_note,
        fill=MUTED,
    )
    canvas.save(out, dpi=(300, 300))
    print(f"{out.name}: {canvas.size}")


row_same_height(
    items=[
        # Power BI: recorte a la fila de tarjetas de plan, donde se lee el precio.
        ("Microsoft Power BI: planes y precios", FIGURAS / "comp_powerbi.png", (60, 400, 1370, 730)),
        ("ThoughtSpot: plan Pro", FIGURAS / "comp_thoughtspot_precio.png", (35, 235, 450, 530)),
    ],
    cell_height=420,
    title="Precios publicados por el propio fabricante",
    out=FIGURAS / "a3_evidencia_precios.png",
)
