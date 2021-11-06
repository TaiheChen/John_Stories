import os
import re
from io import StringIO, BytesIO
from PIL import Image
from PIL import ImageDraw
import pygame

g_script_folder = os.path.dirname(os.path.abspath(__file__))
g_fonts_folder = os.path.join(g_script_folder, "fonts")

g_re_first_word = re.compile((u""
                              + u"(%(prefix)s+\S%(postfix)s+)"  # punctuation
                              + u"|(%(prefix)s*\w+%(postfix)s*)"  # word
                              + u"|(%(prefix)s+\S)|(\S%(postfix)s+)"  # punctuation
                              + u"|(\d+%%)"  # percent
                              ) % {
                                 "prefix": u"['\"\(<\[\{‘“（《「『]",
                                 "postfix": u"[:'\"\)>\]\}：’”）》」』,;\.\?!，、；。？！]",
                             })

pygame.init()

# get font
def getFontForPyGame(font_name="wqy-zenhei.ttc", font_size=14):
    return pygame.font.Font(os.path.join(g_fonts_folder, font_name), font_size)


def makeConfig(cfg=None):
    if not cfg or type(cfg) != dict:
        cfg = {}

    default_cfg = {
        "width": 440,  # px
        "padding": (15, 18, 20, 18),
        "line-height": 20,  # px
        "title-line-height": 32,  # px
        "font-size": 14,  # px
        "title-font-size": 24,  # px
        "font-family": "sarasa-regular.ttc",
        "font-color": (0, 0, 0),
        "font-antialiasing": True,  # font anti-aliasing
        "background-color": (255, 255, 255),
        "border-size": 1,
        "border-color": (192, 192, 192),
        "copyright": u"Copyright@ John",
        "copyright-center": False,  # copyright in center or left
        "first-line-as-title": True, # first line as title
        "break-word": False, # break word or not when make lines
    }
    # update the default config
    default_cfg.update(cfg)
    return default_cfg

#Transfer a sentence to a list
def makeLineToWordsList(line, break_word=False):

    if break_word:
        return [c for c in line]

    lst = []
    while line:
        ro = g_re_first_word.match(line)
        end = 1 if not ro else ro.end()
        lst.append(line[:end])
        line = line[end:]

    return lst

#Divide a long line into several displayable short lines
def makeLongLineToLines(long_line, start_x, start_y, width, line_height, font, cn_char_width=0):

    txt = long_line
    if not txt:
        return [None]
    
    words = makeLineToWordsList(txt)
    lines = []
    if not cn_char_width:
        cn_char_width, h = font.size(u"汉")
    avg_char_per_line = int(width / cn_char_width)
    if avg_char_per_line <= 1:
        avg_char_per_line = 1

    line_x = start_x
    line_y = start_y
    while words:

        tmp_words = words[:avg_char_per_line]
        tmp_ln = "".join(tmp_words)
        w, h = font.size(tmp_ln)
        wc = len(tmp_words)
        while w < width and wc < len(words):
            wc += 1
            tmp_words = words[:wc]
            tmp_ln = "".join(tmp_words)
            w, h = font.size(tmp_ln)
        while w > width and len(tmp_words) > 1:
            tmp_words = tmp_words[:-1]
            tmp_ln = "".join(tmp_words)
            w, h = font.size(tmp_ln)

        if w > width and len(tmp_words) == 1:
            # Assume line_y is a long line
            line_y = makeLongWordToLines(
                tmp_words[0], line_x, line_y, width, line_height, font, lines
            )
            words = words[len(tmp_words):]
            continue

        line = {
            "x": line_x,
            "y": line_y,
            "text": tmp_ln,
            "font": font,
        }

        line_y += line_height
        words = words[len(tmp_words):]

        lines.append(line)

        if len(lines) >= 1:
            # Remove ' ' at the beginning of the second line of a long line
            while len(words) > 0 and not words[0].strip():
                words = words[1:]

    return lines


def makeLongWordToLines(long_word, line_x, line_y, width, line_height, font, lines):
    if not long_word:
        return line_y

    c = long_word[0]
    char_width, char_height = font.size(c)
    default_char_num_per_line = int(width / char_width)

    while long_word:

        tmp_ln = long_word[:default_char_num_per_line]
        w, h = font.size(tmp_ln)

        l = len(tmp_ln)
        while w < width and l < len(long_word):
            l += 1
            tmp_ln = long_word[:l]
            w, h = font.size(tmp_ln)
        while w > width and len(tmp_ln) > 1:
            tmp_ln = tmp_ln[:-1]
            w, h = font.size(tmp_ln)

        l = len(tmp_ln)
        long_word = long_word[l:]

        line = {
            "x": line_x,
            "y": line_y,
            "text": tmp_ln,
            "font": font,
        }

        line_y += line_height
        lines.append(line)

    return line_y

#Make a matrix of lines
def makeMatrix(txt, font, title_font, cfg):
    width = cfg["width"]

    data = {
        "width": width,
        "height": 0,
        "lines": [],
    }

    a = txt.split("\n")
    cur_x = cfg["padding"][3]
    cur_y = cfg["padding"][0]
    cn_char_width, h = font.size(u"汉")

    for ln_idx, ln in enumerate(a):
        ln = ln.rstrip()
        if ln_idx == 0 and cfg["first-line-as-title"]:
            f = title_font
            line_height = cfg["title-line-height"]
        else:
            f = font
            line_height = cfg["line-height"]
        current_width = width - cur_x - cfg["padding"][1]
        lines = makeLongLineToLines(ln, cur_x, cur_y, current_width, line_height, f, cn_char_width=cn_char_width)
        cur_y += line_height * len(lines)

        data["lines"].extend(lines)

    data["height"] = cur_y + cfg["padding"][2]

    return data


def makeImage(data, cfg):
    u"""
    """

    width, height = data["width"], data["height"]
    if cfg["copyright"]:
        height += 48
    im = Image.new("RGB", (width, height), cfg["background-color"])
    dr = ImageDraw.Draw(im)

    for ln_idx, line in enumerate(data["lines"]):
        __makeLine(im, line, cfg)

    drawBorder(im, dr, cfg)
    drawCopyright(im, dr, cfg)

    return im

# Draw copyright information
def drawCopyright(im, dr, cfg):


    if not cfg["copyright"]:
        return

    font = getFontForPyGame(font_name=cfg["font-family"], font_size=12)
    rtext = font.render(cfg["copyright"],
                        cfg["font-antialiasing"], (128, 128, 128), cfg["background-color"]
                        )
    sio = BytesIO()
    pygame.image.save(rtext, sio)
    sio.seek(0)
    copyright_im = Image.open(sio)

    iw, ih = im.size
    cw, ch = rtext.get_size()
    padding = cfg["padding"]

    offset_y = ih - 32 - padding[2]
    if cfg["copyright-center"]:
        cx = (iw - cw) / 2
    else:
        cx = cfg["padding"][3]
    cy = offset_y + 12

    dr.line([(padding[3], offset_y), (iw - padding[1], offset_y)], width=1, fill=(192, 192, 192))
    im.paste(copyright_im, (cx, cy))

# draw the border
def drawBorder(im, dr, cfg):

    if not cfg["border-size"]:
        return

    w, h = im.size
    x, y = w - 1, h - 1
    dr.line(
        [(0, 0), (x, 0), (x, y), (0, y), (0, 0)],
        width=cfg["border-size"],
        fill=cfg["border-color"],
    )

# draw the line in the bottom
def __makeLine(im, line, cfg):
    if not line:
        return

    sio = BytesIO()
    x, y = line["x"], line["y"]
    text = line["text"]
    font = line["font"]
    rtext = font.render(text, cfg["font-antialiasing"], cfg["font-color"], cfg["background-color"])
    pygame.image.save(rtext, sio)

    sio.seek(0)
    ln_im = Image.open(sio)

    im.paste(ln_im, (x, y))

# get the font for pygame and make sure it is compatible with the font
def txt2im(txt, outfn, cfg=None, show=False):
    cfg = makeConfig(cfg)
    font = getFontForPyGame(cfg["font-family"], cfg["font-size"])
    title_font = getFontForPyGame(cfg["font-family"], cfg["title-font-size"])
    data = makeMatrix(txt, font, title_font, cfg)
    im = makeImage(data, cfg)
    im.save(outfn)
    if os.name == "nt" and show:
        im.show()

# generate the image
def generateImg(content, name):
    txt2im(content, name, show=False)


if __name__ == "__main__":
    content = '''title
    content'''
    generateImg(content, 'n.png')