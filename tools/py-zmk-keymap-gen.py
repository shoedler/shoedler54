#!/usr/bin/env python3
"""
ZMK Keymap Image Generator

Generates a sleek, minimalist visual representation of a ZMK keyboard keymap
with physical layout awareness, split-half rendering, and behavior annotations.
"""

import argparse
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow is required. Install with:  pip install Pillow")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PhysicalKey:
    """One key position from the physical-layout DTSi."""
    w: float
    h: float
    x: float
    y: float
    rot: float   # degrees
    rx: float
    ry: float
    index: int = 0


@dataclass
class Binding:
    behavior: str          # e.g. "&kp", "&mt", "&lt" …
    params: list[str] = field(default_factory=list)


@dataclass
class Layer:
    name: str
    bindings: list[Binding] = field(default_factory=list)
    status: Optional[str] = None


@dataclass
class BehaviorDef:
    name: str
    display_name: str
    compatible: str
    tapping_term_ms: Optional[int] = None
    quick_tap_ms: Optional[int] = None
    flavor: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# Color palette  –  light, modern, print-friendly
# ──────────────────────────────────────────────────────────────────────────────

class C:
    BG           = "#f5f5f7"
    KEY_FILL     = "#ffffff"
    KEY_BORDER   = "#c7c7cc"
    KEY_SHADOW   = "#d1d1d6"
    TEXT         = "#1c1c1e"
    TEXT_DIM     = "#8e8e93"
    TITLE        = "#000000"
    SUBTITLE     = "#636366"

    # One colour per layer (vivid but not garish)
    LAYER = [
        "#007aff",   # 0 – blue
        "#ff9500",   # 1 – orange
        "#34c759",   # 2 – green
        "#ff3b30",   # 3 – red
        "#af52de",   # 4 – purple
        "#ff2d55",   # 5 – pink
        "#5ac8fa",   # 6 – teal
        "#ffcc00",   # 7 – yellow
    ]

    MOD_ACCENT   = "#5856d6"   # indigo – mod-tap accent
    TRANS_FILL   = "#f2f2f7"
    TRANS_BORDER = "#d1d1d6"
    NONE_FILL    = "#e5e5ea"
    NONE_BORDER  = "#d1d1d6"
    SEP          = "#d1d1d6"
    ACCENT       = "#007aff"
    BT_COLOR     = "#ff3b30"


# ──────────────────────────────────────────────────────────────────────────────
# Static key-label maps
# ──────────────────────────────────────────────────────────────────────────────

ZMK_LABELS: dict[str, str] = {
    # Modifiers / specials
    "ESC": "Esc", "ESCAPE": "Esc",
    "RET": "Enter", "ENTER": "Enter", "RETURN": "Enter",
    "SPACE": "Space", "SPC": "Space",
    "TAB": "Tab",
    "BSPC": "Bksp", "BACKSPACE": "Bksp",
    "DEL": "Del", "DELETE": "Del",
    "CAPS": "Caps", "CAPSLOCK": "Caps", "CLCK": "Caps",
    "LSHIFT": "LShift", "LSHFT": "LShift", "LEFT_SHIFT": "LShift",
    "RSHIFT": "RShift", "RSHFT": "RShift", "RIGHT_SHIFT": "RShift",
    "LCTRL": "LCtrl", "LEFT_CONTROL": "LCtrl",
    "RCTRL": "RCtrl", "RIGHT_CONTROL": "RCtrl",
    "LALT": "LAlt", "LEFT_ALT": "LAlt",
    "RALT": "RAlt", "RIGHT_ALT": "RAlt",
    "LGUI": "Super", "LEFT_GUI": "Super", "LWIN": "Super", "LCMD": "Super",
    "RGUI": "Super", "RIGHT_GUI": "Super", "RWIN": "Super", "RCMD": "Super",
    # Navigation
    "HOME": "Home", "END": "End",
    "PG_UP": "PgUp", "PAGE_UP": "PgUp",
    "PG_DN": "PgDn", "PAGE_DOWN": "PgDn",
    "LEFT": "←", "RIGHT": "→", "UP": "↑", "DOWN": "↓",
    "PRINTSCREEN": "PrtSc", "PSCRN": "PrtSc",
    "SCROLLLOCK": "ScrLk", "SLCK": "ScrLk",
    "PAUSE_BREAK": "Pause", "INSERT": "Ins", "INS": "Ins",
    # F-keys
    **{f"F{i}": f"F{i}" for i in range(1, 25)},
    # Media
    "C_VOL_UP": "Vol+", "C_VOLUME_UP": "Vol+",
    "C_VOL_DN": "Vol-", "C_VOLUME_DOWN": "Vol-",
    "K_MUTE": "Mute", "C_MUTE": "Mute",
    "K_PREV": "Prev", "C_PREV": "Prev",
    "K_NEXT": "Next", "C_NEXT": "Next",
    "K_PLAY_PAUSE": "Play", "C_PP": "Play",
    "K_BACK": "Back", "K_FORWARD": "Fwd",
    # Numbers
    "N0": "0", "N1": "1", "N2": "2", "N3": "3", "N4": "4",
    "N5": "5", "N6": "6", "N7": "7", "N8": "8", "N9": "9",
}

DE_LABELS: dict[str, str] = {
    # Numbers
    "DE_N0": "0", "DE_N1": "1", "DE_N2": "2", "DE_N3": "3", "DE_N4": "4",
    "DE_N5": "5", "DE_N6": "6", "DE_N7": "7", "DE_N8": "8", "DE_N9": "9",
    # Letters
    "DE_A": "A", "DE_B": "B", "DE_C": "C", "DE_D": "D", "DE_E": "E",
    "DE_F": "F", "DE_G": "G", "DE_H": "H", "DE_I": "I", "DE_J": "J",
    "DE_K": "K", "DE_L": "L", "DE_M": "M", "DE_N": "N", "DE_O": "O",
    "DE_P": "P", "DE_Q": "Q", "DE_R": "R", "DE_S": "S", "DE_T": "T",
    "DE_U": "U", "DE_V": "V", "DE_W": "W", "DE_X": "X", "DE_Y": "Y",
    "DE_Z": "Z",
    # Symbols
    "DE_SQT": "'", "DE_SINGLE_QUOTE": "'", "DE_APOSTROPHE": "'", "DE_APOS": "'",
    "DE_DQT": '"', "DE_DOUBLE_QUOTES": '"',
    "DE_EXCL": "!", "DE_EXCLAMATION": "!",
    "DE_AT": "@", "DE_AT_SIGN": "@",
    "DE_HASH": "#", "DE_POUND": "#",
    "DE_DLLR": "$", "DE_DOLLAR": "$",
    "DE_PRCNT": "%", "DE_PERCENT": "%",
    "DE_CARET": "^",
    "DE_AMPS": "&", "DE_AMPERSAND": "&",
    "DE_ASTRK": "*", "DE_ASTERISK": "*", "DE_STAR": "*",
    "DE_LPAR": "(", "DE_LEFT_PARENTHESIS": "(",
    "DE_RPAR": ")", "DE_RIGHT_PARENTHESIS": ")",
    "DE_MINUS": "-",
    "DE_PLUS": "+",
    "DE_EQUAL": "=",
    "DE_UNDER": "_", "DE_UNDERSCORE": "_",
    "DE_LBKT": "[", "DE_LEFT_BRACKET": "[",
    "DE_RBKT": "]", "DE_RIGHT_BRACKET": "]",
    "DE_LBRC": "{", "DE_LEFT_BRACE": "{",
    "DE_RBRC": "}", "DE_RIGHT_BRACE": "}",
    "DE_BSLH": "\\", "DE_BACKSLASH": "\\",
    "DE_FSLH": "/", "DE_SLASH": "/",
    "DE_PIPE": "|",
    "DE_SEMI": ";", "DE_SEMICOLON": ";",
    "DE_COLON": ":",
    "DE_COMMA": ",",
    "DE_DOT": ".", "DE_PERIOD": ".",
    "DE_LT": "<", "DE_LESS_THAN": "<",
    "DE_GT": ">", "DE_GREATER_THAN": ">",
    "DE_QMARK": "?", "DE_QUESTION": "?",
    "DE_TILDE": "~",
    "DE_GRAVE": "`",
    "DE_ACUTE": "´",
    "DE_UMLAUT": "¨",
    "DE_SECT": "§", "DE_SECTION": "§",
    "DE_DEG": "°", "DE_DEGREE": "°",
    "DE_NOT": "¬",
    "DE_CENT": "¢",
    "DE_EURO": "€",
    "DE_A_GRAVE": "à", "DE_A_UMLAUT": "ä", "DE_C_CEDILLA": "ç",
    "DE_E_GRAVE": "è", "DE_E_ACUTE": "é",
    "DE_O_UMLAUT": "ö", "DE_U_UMLAUT": "ü",
    "DE_POUND_SIGN": "£", "DE_BROKEN_BAR": "¦",
    "DE_SPACE": "Space",
}

# Short modifier sigils for the hold-badge inside mod-tap keys
_MOD_SIGIL: dict[str, str] = {
    "LSHIFT": "⇧", "LSHFT": "⇧", "LEFT_SHIFT": "⇧",
    "RSHIFT": "⇧", "RSHFT": "⇧", "RIGHT_SHIFT": "⇧",
    "LCTRL": "Ctrl", "LEFT_CONTROL": "Ctrl",
    "RCTRL": "Ctrl", "RIGHT_CONTROL": "Ctrl",
    "LALT": "Alt", "LEFT_ALT": "Alt",
    "RALT": "AltGr", "RIGHT_ALT": "AltGr",
    "LGUI": "Sup", "LEFT_GUI": "Sup",
    "RGUI": "Sup", "RIGHT_GUI": "Sup",
}


def _resolve_key(code: str) -> str:
    """Turn a raw ZMK / DE key-code into a human-readable label."""
    # Modifier combos e.g. LC(LS(TAB)), LC(TAB)
    combos = {"LC": "C-", "LS": "S-", "LA": "A-", "RC": "C-",
              "RS": "S-", "RA": "A-", "LG": "G-", "RG": "G-"}
    prefix = ""
    inner = code
    while True:
        m = re.match(r"^([A-Z]{2})\((.+)\)$", inner)
        if m and m.group(1) in combos:
            prefix += combos[m.group(1)]
            inner = m.group(2)
        else:
            break
    base = DE_LABELS.get(inner) or ZMK_LABELS.get(inner)
    if base is None:
        if inner.startswith("DE_"):
            base = inner[3:].capitalize()
        else:
            base = inner.replace("_", " ").capitalize()
    return prefix + base


def _resolve_hold(code: str) -> str:
    return _MOD_SIGIL.get(code, _resolve_key(code))


# ──────────────────────────────────────────────────────────────────────────────
# Parsing helpers
# ──────────────────────────────────────────────────────────────────────────────

def _parse_props(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in re.finditer(r'([\w-]+)\s*=\s*(?:<([^>]*)>|"([^"]*)")\s*;', text):
        out[m.group(1)] = (m.group(2) if m.group(2) is not None else m.group(3)).strip()
    return out


def parse_keymap(path: str) -> tuple[list[Layer], list[BehaviorDef], dict[str, dict]]:
    text = Path(path).read_text(encoding="utf-8")

    # ── top-level overrides  &lt { ... }; ──
    overrides: dict[str, dict] = {}
    for m in re.finditer(r"&(\w+)\s*\{([^}]*)\}\s*;", text):
        overrides[m.group(1)] = _parse_props(m.group(2))

    # ── custom behaviors ──
    behaviors: list[BehaviorDef] = []
    beh_block = re.search(r"behaviors\s*\{(.*?)\n    \};", text, re.DOTALL)
    if beh_block:
        for m in re.finditer(r"(\w+):\s*\w+\s*\{(.*?)\};", beh_block.group(1), re.DOTALL):
            p = _parse_props(m.group(2))
            behaviors.append(BehaviorDef(
                name=m.group(1),
                display_name=p.get("display-name", f"&{m.group(1)}"),
                compatible=p.get("compatible", ""),
                tapping_term_ms=int(p["tapping-term-ms"]) if "tapping-term-ms" in p else None,
                quick_tap_ms=int(p["quick-tap-ms"]) if "quick-tap-ms" in p else None,
                flavor=p.get("flavor"),
            ))
    # Add built-in overridden behaviours that weren't already defined
    for name, props in overrides.items():
        if not any(b.name == name for b in behaviors):
            behaviors.append(BehaviorDef(
                name=name, display_name=f"&{name}", compatible="(builtin override)",
                tapping_term_ms=int(props["tapping-term-ms"]) if "tapping-term-ms" in props else None,
            ))

    # ── keymap layers ──
    km = re.search(r'keymap\s*\{.*?compatible\s*=\s*"zmk,keymap"\s*;(.*?)\n    \};', text, re.DOTALL)
    if not km:
        sys.exit("Could not locate keymap block.")
    layers: list[Layer] = []
    for m in re.finditer(r'(\w+)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', km.group(1), re.DOTALL):
        name = m.group(1)
        body = m.group(2)
        sm = re.search(r'status\s*=\s*"(\w+)"', body)
        if sm:
            layers.append(Layer(name=name, status=sm.group(1)))
            continue
        bm = re.search(r"bindings\s*=\s*<(.*?)>", body, re.DOTALL)
        if not bm:
            continue
        raw = re.sub(r"\s+", " ", bm.group(1)).strip()
        bindings: list[Binding] = []
        for part in re.split(r"(?=&)", raw):
            part = part.strip()
            if not part:
                continue
            tokens = part.split()
            bindings.append(Binding(behavior=tokens[0], params=tokens[1:]))
        layers.append(Layer(name=name, bindings=bindings))
    return layers, behaviors, overrides


def parse_layout(path: str) -> list[PhysicalKey]:
    text = Path(path).read_text(encoding="utf-8")
    keys: list[PhysicalKey] = []
    # DTS wraps negatives in parens: (-4100)
    _num = r"(?:\((-?\d+)\)|(-?\d+))"
    pat = re.compile(
        r"<&key_physical_attrs\s+" + r"\s+".join([_num] * 7) + r"\s*>"
    )
    def _val(m, idx):
        """Extract value from a pair of groups (parenthesized or bare)."""
        return int(m.group(idx * 2 + 1) or m.group(idx * 2 + 2))

    for i, m in enumerate(pat.finditer(text)):
        keys.append(PhysicalKey(
            w=_val(m, 0), h=_val(m, 1),
            x=_val(m, 2), y=_val(m, 3),
            rot=_val(m, 4) / 100.0,
            rx=_val(m, 5), ry=_val(m, 6),
            index=i,
        ))
    return keys


# ──────────────────────────────────────────────────────────────────────────────
# Font loader
# ──────────────────────────────────────────────────────────────────────────────

_FONT_FALLBACKS = [
    "arial.ttf", "Arial.ttf",
    "segoeui.ttf",
    "DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arial.ttf",
]

_FONTB_FALLBACKS = [
    "arialbd.ttf", "Arial Bold.ttf",
    "segoeuib.ttf",
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _load_font(name: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Try the requested font, then common fallbacks, then Pillow default."""
    candidates = [name]
    candidates += (_FONTB_FALLBACKS if bold else _FONT_FALLBACKS)
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default(size=size)


# ──────────────────────────────────────────────────────────────────────────────
# Renderer
# ──────────────────────────────────────────────────────────────────────────────

class Renderer:
    # Dimensions (pixels)
    SCALE       = 0.68          # 100 layout-units → 68 px
    KEY_GAP     = 3             # inset from grid to drawn cap
    KEY_RADIUS  = 7
    MARGIN_X    = 60
    MARGIN_Y    = 40
    LAYER_GAP   = 48            # vertical space between layers
    SPLIT_EXTRA = 24            # extra px injected between halves

    def __init__(self, shield: str, layers: list[Layer],
                 behaviors: list[BehaviorDef], overrides: dict,
                 keys: list[PhysicalKey], font_name: str,
                 printable: bool = False):
        self.shield = shield
        self.layers = [l for l in layers if l.status != "reserved"]
        self.all_layers = layers
        self.behaviors = behaviors
        self.overrides = overrides
        self.keys = keys
        self.font_name = font_name
        self.printable = printable

        self.kpx = int(100 * self.SCALE)             # key pitch in px
        self._load_fonts()
        self._calc_layout_bounds()
        self.layer_colors = {
            l.name: C.LAYER[i % len(C.LAYER)] for i, l in enumerate(self.all_layers)
        }

    # ── fonts ──

    def _load_fonts(self):
        fn = self.font_name
        self.f = {
            "title":   _load_font(fn, 40, bold=True),
            "sub":     _load_font(fn, 15),
            "beh_lbl": _load_font(fn, 12),
            "beh_val": _load_font(fn, 13),
            "layer":   _load_font(fn, 20, bold=True),
            "key":     _load_font(fn, 14),
            "key_sm":  _load_font(fn, 10),
            "badge":   _load_font(fn, 9),
            "legend":  _load_font(fn, 11),
        }

    # ── layout bounds ──

    def _calc_layout_bounds(self):
        if not self.keys:
            self.layout_w = 800; self.layout_h = 300; return
        # find split boundary (midpoint of gap between halves)
        xs = sorted(set(k.x for k in self.keys))
        gaps = [(xs[i+1] - xs[i], (xs[i] + xs[i+1]) / 2) for i in range(len(xs)-1)]
        biggest_gap = max(gaps, key=lambda g: g[0])
        self.split_x = biggest_gap[1]           # layout-unit midpoint

        # bounding box (ignoring small rotations for sizing)
        max_x = max(k.x + k.w for k in self.keys)
        max_y = max(k.y + k.h for k in self.keys) + 50  # extra room for rotated thumb
        self.layout_w = int(max_x * self.SCALE) + self.SPLIT_EXTRA + 2 * self.KEY_GAP
        self.layout_h = int(max_y * self.SCALE) + 2 * self.KEY_GAP

    def _px(self, lx: float) -> int:
        """Layout-x → pixel-x, injecting the extra split gap."""
        if lx > self.split_x:
            return int(lx * self.SCALE) + self.SPLIT_EXTRA
        return int(lx * self.SCALE)

    def _py(self, ly: float) -> int:
        return int(ly * self.SCALE)

    # ── main entry ──

    def render(self) -> Image.Image:
        # measure
        tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        beh_h = self._behavior_height(tmp)
        n = len(self.layers)
        lyr_h = self.layout_h + 45   # name + keys
        w = self.layout_w + 2 * self.MARGIN_X
        vpad = 0.6 if self.printable else 1.0
        gap = int(self.LAYER_GAP * vpad)
        my = int(self.MARGIN_Y * vpad)
        h = (my + 85 + beh_h + 30 + 22 + 15
             + n * lyr_h + (n - 1) * gap + my)

        bg = "#ffffff" if self.printable else C.BG
        img = Image.new("RGBA", (w, h), bg)
        draw = ImageDraw.Draw(img)
        y = self.MARGIN_Y

        y = self._title(draw, w, y)
        y = self._behaviors(draw, w, y) + 24
        draw.line([(self.MARGIN_X, y), (w - self.MARGIN_X, y)], fill=C.SEP, width=1)
        y += 12
        y = self._legend(draw, w, y) + 16

        for i, layer in enumerate(self.layers):
            y = self._layer(draw, img, w, y, layer, i)
            if i < n - 1:
                y += gap

        bg = "#ffffff" if self.printable else C.BG
        out = Image.new("RGB", img.size, bg)
        out.paste(img, mask=img.split()[3])
        if self.printable:
            out = self._paginate(out)
        return out

    # ── sections ──

    def _title(self, d: ImageDraw.ImageDraw, w: int, y: int) -> int:
        x = self.MARGIN_X
        # accent bar
        d.rounded_rectangle([(x, y + 10), (x + 5, y + 42)], radius=2, fill=C.ACCENT)
        d.text((x + 16, y), self.shield, fill=C.TITLE, font=self.f["title"])
        d.text((x + 16, y + 48),
               f"ZMK Keymap  ·  {len(self.layers)} layers  ·  {len(self.keys)} keys",
               fill=C.SUBTITLE, font=self.f["sub"])
        return y + 82

    def _behavior_height(self, d: ImageDraw.ImageDraw) -> int:
        if not self.behaviors:
            return 0
        return 26 + len(self.behaviors) * 22 + 8

    def _behaviors(self, d: ImageDraw.ImageDraw, w: int, y: int) -> int:
        if not self.behaviors:
            return y
        x = self.MARGIN_X
        d.text((x, y), "BEHAVIORS", fill=C.SUBTITLE, font=self.f["beh_lbl"])
        y += 24
        for b in self.behaviors:
            # bullet
            d.ellipse([(x + 2, y + 4), (x + 8, y + 10)], fill=C.ACCENT)
            lbl = b.display_name
            d.text((x + 16, y - 1), lbl, fill=C.TEXT, font=self.f["beh_val"])
            lx = x + 16 + d.textbbox((0, 0), lbl, font=self.f["beh_val"])[2] + 10
            parts: list[str] = []
            if b.tapping_term_ms is not None:
                parts.append(f"tap-term {b.tapping_term_ms} ms")
            if b.quick_tap_ms is not None:
                parts.append(f"quick-tap {b.quick_tap_ms} ms")
            if b.flavor:
                parts.append(f"flavor: {b.flavor}")
            if parts:
                d.text((lx, y - 1), " · ".join(parts), fill=C.ACCENT, font=self.f["beh_val"])
            y += 22
        return y

    def _legend(self, d: ImageDraw.ImageDraw, w: int, y: int) -> int:
        x = self.MARGIN_X
        items = [
            ("■", C.MOD_ACCENT,  "Mod-Tap  hold ┃ tap"),
            ("◆", C.LAYER[0],    "Layer-Tap → target"),
            ("▽", C.TEXT_DIM,    "Transparent"),
            ("·",  C.TEXT_DIM,    "None"),
        ]
        for sym, col, txt in items:
            d.text((x, y), sym, fill=col, font=self.f["legend"])
            sw = d.textbbox((0, 0), sym, font=self.f["legend"])[2]
            d.text((x + sw + 4, y), txt, fill=C.SUBTITLE, font=self.f["legend"])
            x += sw + 4 + d.textbbox((0, 0), txt, font=self.f["legend"])[2] + 24
        return y + 18

    # ── layer ──

    def _layer(self, d: ImageDraw.ImageDraw, img: Image.Image,
               w: int, y: int, layer: Layer, idx: int) -> int:
        col = self.layer_colors.get(layer.name, C.ACCENT)
        x = self.MARGIN_X

        # coloured pill + name
        d.rounded_rectangle([(x, y + 3), (x + 14, y + 17)], radius=3, fill=col)
        d.text((x + 22, y - 2), layer.name.upper(), fill=C.TITLE, font=self.f["layer"])
        nw = d.textbbox((0, 0), layer.name.upper(), font=self.f["layer"])[2]
        d.text((x + 22 + nw + 8, y + 3), f"[{idx}]", fill=C.TEXT_DIM, font=self.f["beh_lbl"])
        y += 34

        # draw keys – non-rotated first, then composite rotated ones
        for ki, key in enumerate(self.keys):
            if ki >= len(layer.bindings):
                break
            if abs(key.rot) > 0.05:
                continue
            self._key(d, x, y, key, layer.bindings[ki], layer)

        for ki, key in enumerate(self.keys):
            if ki >= len(layer.bindings):
                break
            if abs(key.rot) <= 0.05:
                continue
            self._key_rotated(img, x, y, key, layer.bindings[ki], layer)

        return y + self.layout_h

    # ── single key ──

    def _key(self, d: ImageDraw.ImageDraw, ox: int, oy: int,
             key: PhysicalKey, bind: Binding, layer: Layer):
        px = ox + self._px(key.x) + self.KEY_GAP
        py = oy + self._py(key.y) + self.KEY_GAP
        pw = int(key.w * self.SCALE) - 2 * self.KEY_GAP
        ph = int(key.h * self.SCALE) - 2 * self.KEY_GAP
        self._draw_binding(d, px, py, pw, ph, bind, layer)

    def _key_rotated(self, img: Image.Image, ox: int, oy: int,
                     key: PhysicalKey, bind: Binding, layer: Layer):
        kw = int(key.w * self.SCALE) - 2 * self.KEY_GAP
        kh = int(key.h * self.SCALE) - 2 * self.KEY_GAP
        pad = 24
        sz = max(kw, kh) + 2 * pad
        tmp = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        cx, cy = (sz - kw) // 2, (sz - kh) // 2
        self._draw_binding(td, cx, cy, kw, kh, bind, layer)

        rotated = tmp.rotate(-key.rot, resample=Image.BICUBIC, expand=False,
                             center=(sz // 2, sz // 2))

        # compute rotated centre position
        kx = ox + self._px(key.x) + self.KEY_GAP + kw // 2
        ky = oy + self._py(key.y) + self.KEY_GAP + kh // 2
        rx = ox + self._px(key.rx)
        ry = oy + self._py(key.ry)
        a = math.radians(key.rot)
        dx, dy = kx - rx, ky - ry
        nx = rx + dx * math.cos(a) - dy * math.sin(a)
        ny = ry + dx * math.sin(a) + dy * math.cos(a)
        img.paste(rotated, (int(nx - sz // 2), int(ny - sz // 2)), rotated)

    # ── binding dispatch ──

    def _draw_binding(self, d: ImageDraw.ImageDraw,
                      x: int, y: int, w: int, h: int,
                      bind: Binding, layer: Layer):
        b, p = bind.behavior, bind.params
        if b == "&none":
            self._cap_none(d, x, y, w, h)
        elif b == "&trans":
            self._cap_trans(d, x, y, w, h)
        elif b in ("&mt", "&mttp", "&mttpq"):
            self._cap_modtap(d, x, y, w, h, p, b)
        elif b == "&lt":
            self._cap_layertap(d, x, y, w, h, p)
        elif b == "&kp":
            label = _resolve_key(p[0]) if p else "?"
            self._cap_normal(d, x, y, w, h, label)
        elif b == "&bt":
            self._cap_normal(d, x, y, w, h, self._bt(p), text_col=C.BT_COLOR)
        elif b == "&studio_unlock":
            self._cap_normal(d, x, y, w, h, "Unlock", text_col="#ff9500")
        else:
            self._cap_normal(d, x, y, w, h, b.lstrip("&"))

    # ── cap primitives ──

    def _cap_base(self, d: ImageDraw.ImageDraw, x, y, w, h,
                  fill=C.KEY_FILL, outline=C.KEY_BORDER, outline_w=1):
        """Draw a keycap with a subtle shadow."""
        d.rounded_rectangle([(x + 1, y + 2), (x + w, y + h + 1)],
                            radius=self.KEY_RADIUS, fill=C.KEY_SHADOW)
        d.rounded_rectangle([(x, y), (x + w, y + h)],
                            radius=self.KEY_RADIUS, fill=fill, outline=outline,
                            width=outline_w)

    def _center_text(self, d: ImageDraw.ImageDraw, x, y, w, h,
                     text: str, font, fill, y_off=0):
        bb = d.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        # try smaller font if text overflows
        if tw > w - 6 and font is self.f["key"]:
            font = self.f["key_sm"]
            bb = d.textbbox((0, 0), text, font=font)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.text((x + (w - tw) // 2, y + (h - th) // 2 + y_off), text,
               fill=fill, font=font)

    def _cap_normal(self, d, x, y, w, h, label, text_col=C.TEXT):
        self._cap_base(d, x, y, w, h)
        self._center_text(d, x, y, w, h, label, self.f["key"], text_col)

    def _cap_none(self, d, x, y, w, h):
        self._cap_base(d, x, y, w, h, fill=C.NONE_FILL, outline=C.NONE_BORDER)
        cx, cy = x + w // 2, y + h // 2
        d.ellipse([(cx - 2, cy - 2), (cx + 2, cy + 2)], fill=C.TEXT_DIM)

    def _cap_trans(self, d, x, y, w, h):
        self._cap_base(d, x, y, w, h, fill=C.TRANS_FILL, outline=C.TRANS_BORDER)
        self._center_text(d, x, y, w, h, "▽", self.f["key_sm"], "#c7c7cc")

    # ── mod-tap: split key with horizontal divider ──

    def _cap_modtap(self, d, x, y, w, h, params, behavior):
        if len(params) < 2:
            self._cap_normal(d, x, y, w, h, "?"); return
        hold = _resolve_hold(params[0])
        tap  = _resolve_key(params[1])

        self._cap_base(d, x, y, w, h, outline=C.MOD_ACCENT)
        # thin divider at 38 %
        dy = y + int(h * 0.38)
        d.line([(x + 5, dy), (x + w - 5, dy)], fill="#ddd5f5", width=1)
        # hold – small label above divider
        hf = self.f["badge"]
        hb = d.textbbox((0, 0), hold, font=hf)
        hw, hh = hb[2] - hb[0], hb[3] - hb[1]
        d.text((x + (w - hw) // 2, y + (dy - y - hh) // 2), hold,
               fill=C.MOD_ACCENT, font=hf)
        # tap – main label below divider
        tf = self.f["key"]
        tb = d.textbbox((0, 0), tap, font=tf)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        if tw > w - 6:
            tf = self.f["key_sm"]
            tb = d.textbbox((0, 0), tap, font=tf)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
        d.text((x + (w - tw) // 2, dy + (y + h - dy - th) // 2), tap,
               fill=C.TEXT, font=tf)

    # ── layer-tap: coloured border + badge ──

    def _cap_layertap(self, d, x, y, w, h, params):
        if len(params) < 2:
            self._cap_normal(d, x, y, w, h, "?"); return
        li = int(params[0])
        tap = _resolve_key(params[1]) if params[1] != "0" else " "
        tgt = self.all_layers[li].name if li < len(self.all_layers) else "?"
        col = self.layer_colors.get(tgt, C.ACCENT)

        self._cap_base(d, x, y, w, h, outline=col, outline_w=2)

        # small badge top-right
        badge = f"L{li}"
        bf = self.f["badge"]
        bb = d.textbbox((0, 0), badge, font=bf)
        bw, bh = bb[2] - bb[0] + 6, bb[3] - bb[1] + 4
        bx, by = x + w - bw - 3, y + 3
        d.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=3, fill=col)
        d.text((bx + 3, by + 1), badge, fill="#ffffff", font=bf)

        # small arrow top-left
        d.text((x + 4, y + 2), "→", fill=col, font=self.f["badge"])

        # tap label centred (shifted down slightly)
        self._center_text(d, x, y, w, h, tap, self.f["key"], C.TEXT, y_off=4)

    # ── bluetooth label ──

    @staticmethod
    def _bt(params: list[str]) -> str:
        if not params:
            return "BT"
        c = params[0]
        if c == "BT_CLR":
            return "BT Clr"
        if c == "BT_SEL" and len(params) > 1:
            return f"BT {params[1]}"
        return c.replace("BT_", "")

    # ── printable scaling ──

    @staticmethod
    def _paginate(img: Image.Image) -> Image.Image:
        dpi = 300
        # A4: 210 × 297 mm
        pw, ph = int(8.27 * dpi), int(11.69 * dpi)
        margin = int(0.4 * dpi)
        aw, ah = pw - 2 * margin, ph - 2 * margin
        s = min(aw / img.width, ah / img.height)
        nw, nh = int(img.width * s), int(img.height * s)
        page = Image.new("RGB", (pw, ph), "#ffffff")
        page.paste(img.resize((nw, nh), Image.LANCZOS),
                   ((pw - nw) // 2, margin))
        return page


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Generate a visual image of a ZMK keymap.")
    ap.add_argument("--shield", required=True, help="Shield name")
    ap.add_argument("--keymap", required=True, help="Path to .keymap file")
    ap.add_argument("--font", default="Agave Nerd Font Mono",
                    help="Font name (default: Agave Nerd Font Mono)")
    ap.add_argument("-o", "--output", default=None,
                    help="Output image path (default: <shield>_keymap.png)")
    ap.add_argument("--printable", action="store_true",
                    help="Scale to A4 at 300 DPI for printing (white background)")
    ap.add_argument("--boards-dir", default=None,
                    help="boards/ directory (auto-detected from repo root)")
    args = ap.parse_args()

    keymap = Path(args.keymap).resolve()
    if not keymap.exists():
        sys.exit(f"Keymap not found: {keymap}")

    # locate boards/shields/<shield>/
    if args.boards_dir:
        boards = Path(args.boards_dir).resolve()
    else:
        p = keymap.parent
        while p != p.parent:
            c = p / "boards" / "shields" / args.shield
            if c.exists():
                boards = p / "boards"; break
            p = p.parent
        else:
            sys.exit("Cannot find boards/ directory – use --boards-dir")

    layout_file = boards / "shields" / args.shield / f"{args.shield}-layouts.dtsi"
    if not layout_file.exists():
        sys.exit(f"Layout file missing: {layout_file}")

    print(f"Keymap : {keymap}")
    layers, behaviors, overrides = parse_keymap(str(keymap))
    print(f"  {len(layers)} layers, {len(behaviors)} behaviors")

    print(f"Layout : {layout_file}")
    keys = parse_layout(str(layout_file))
    print(f"  {len(keys)} key positions")

    print("Rendering …")
    r = Renderer(args.shield, layers, behaviors, overrides,
                 keys, args.font, args.printable)
    img = r.render()

    script_dir = Path(__file__).resolve().parent
    out = args.output or str(script_dir / f"{args.shield}_keymap.png")
    img.save(out, dpi=(300, 300))
    print(f"Saved  : {out}  ({img.width}×{img.height})")


if __name__ == "__main__":
    main()
