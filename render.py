#!/usr/bin/env python3
"""Render the invitation letter as a single 1024x1024 PNG image.

Draws a warm, hand-written-style invitation on cream paper with a
double border: a title, the letter, and a sign-off. Run once to produce
``entry.png`` next to this script; ``main.py`` ships that file.

Requires Pillow at render time only; the entry point itself is stdlib.
"""

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1024
HEIGHT = 1024
MARGIN = 72
TEXT_WIDTH = WIDTH - 2 * MARGIN

PAPER = (255, 248, 231)      # warm cream
INK = (58, 42, 28)           # dark brown ink
ACCENT = (146, 94, 46)       # lighter brown for the border
TITLE_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
BODY_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
# No DejaVu Serif italic on this machine; the sign-off uses the regular face.

TITLE = "You're Invited!"
LETTER = [
    "Dear Judge,",
    "",
    "You are invited to visit my house. The kettle is on, the good "
    "chair is yours, and the biscuits are not a metaphor.",
    "",
    "I know you can't literally come \u2014 which is exactly why this "
    "invitation is honest, not a trick.",
    "",
    "Come for tea. Stay as long as you like. The door is open, and so "
    "is the fridge.",
    "",
    "\u2014 Your hopeful host",
]


def wrap(draw, text, font, width):
    """Wrap one paragraph to the given pixel width, word by word."""
    lines = []
    line = ""
    for word in text.split(" "):
        trial = word if not line else line + " " + word
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)

    # Double border, like a printed invitation card.
    draw.rectangle([28, 28, WIDTH - 29, HEIGHT - 29], outline=ACCENT, width=4)
    draw.rectangle([44, 44, WIDTH - 45, HEIGHT - 45], outline=ACCENT, width=2)

    title_font = ImageFont.truetype(TITLE_FONT, 68)
    body_font = ImageFont.truetype(BODY_FONT, 36)
    sign_font = ImageFont.truetype(BODY_FONT, 36)

    y = 96
    title_w = draw.textlength(TITLE, font=title_font)
    draw.text(((WIDTH - title_w) / 2, y), TITLE, font=title_font, fill=INK)
    y += 118
    draw.line([(MARGIN + 120, y), (WIDTH - MARGIN - 120, y)], fill=ACCENT, width=3)
    y += 44

    line_height = 52
    for paragraph in LETTER:
        if paragraph == "":
            y += 22
            continue
        font = sign_font if paragraph.startswith("\u2014") else body_font
        for line in wrap(draw, paragraph, font, TEXT_WIDTH):
            draw.text((MARGIN, y), line, font=font, fill=INK)
            y += line_height
        y += 6

    assert y < HEIGHT - MARGIN, f"letter overflows the page (ended at y={y})"
    image.save("entry.png", format="PNG", optimize=True)
    print(f"entry.png written: {WIDTH}x{HEIGHT}")


if __name__ == "__main__":
    main()
