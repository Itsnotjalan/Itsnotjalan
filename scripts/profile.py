#!/usr/bin/env python3
"""itsnotjalan · GitHub profile builder.

    python3 scripts/profile.py              build assets/*.svg (static panels)
                                            and dist/signal.svg (live stats, needs GITHUB_TOKEN)
    python3 scripts/profile.py --static     static panels only
    python3 scripts/profile.py --data f.json   live panel from a local JSON (preview)

Standard library only. Every panel uses the same drawing kit (atmosphere,
frosted-glass cards, window frame) so the stacked SVGs read as one interface.
To change a text, edit the section functions below and push: the workflow
rebuilds the panels.
"""
import datetime
import json
import math
import os
import random
import sys
import urllib.request
from xml.sax.saxutils import escape

W = 1000
C = {
    'bg': '#0B0907', 'cream': '#F1E4CF', 'sand': '#C4A98B', 'umber': '#8C7A63',
    'brown': '#62492F', 'line': '#3A2C1F', 'rose': '#A5716A', 'glow': '#F6E7CF',
}
MONO = "SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace"
SERIF = "Georgia,'Times New Roman',serif"

ICONS = {
 "computer": "<rect x=\"3\" y=\"4\" width=\"18\" height=\"12.5\" rx=\"2\"/><path d=\"M12 16.5V20M8 20h8\"/>",
 "ai": "<path d=\"M11 3.5C11.6 7.6 13.7 9.7 17.8 10.3 13.7 10.9 11.6 13 11 17.1 10.4 13 8.3 10.9 4.2 10.3 8.3 9.7 10.4 7.6 11 3.5Z\"/><path d=\"M18 14.6c.25 1.45.95 2.15 2.4 2.4-1.45.25-2.15.95-2.4 2.4-.25-1.45-.95-2.15-2.4-2.4 1.45-.25 2.15-.95 2.4-2.4Z\"/>",
 "guitar": "<g transform=\"translate(12 12) scale(0.9) rotate(40) translate(-12 -13.2)\"><path d=\"M12 11.4C9.37 11.4 7.75 12.19 7.75 14.57C7.75 16.17 9.00 16.17 9.00 17.47C9.00 18.90 6.40 18.90 6.40 20.64C6.40 22.83 8.91 24.6 12 24.6C15.09 24.6 17.60 22.83 17.60 20.64C17.60 18.90 15.00 18.90 15.00 17.47C15.00 16.17 16.25 16.17 16.25 14.57C16.25 12.19 14.63 11.4 12 11.4Z\"/><path d=\"M12 11.4V5.4\"/><path d=\"M10.85 5.4h2.3l.38-3.5a.62.62 0 0 0-.62-.7h-1.82a.62.62 0 0 0-.62.7z\"/><circle cx=\"12\" cy=\"16.37\" r=\"1.3\"/><path d=\"M10.4 22.54h3.2\"/></g>",
 "os": "<rect x=\"3\" y=\"4\" width=\"18\" height=\"16\" rx=\"2\"/><path d=\"M3 8.2h18M7 12l2.5 2.4L7 16.8M12.5 16.8h4.5\"/>",
 "code": "<path d=\"M8 7l-5 5 5 5M16 7l5 5-5 5M13.8 4.6l-3.6 14.8\"/>",
 "web": "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18\"/>",
 "db": "<ellipse cx=\"12\" cy=\"6\" rx=\"8\" ry=\"3\"/><path d=\"M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3\"/>",
 "cpu": "<rect x=\"6\" y=\"6\" width=\"12\" height=\"12\" rx=\"1.6\"/><rect x=\"9.5\" y=\"9.5\" width=\"5\" height=\"5\" rx=\".6\"/><path d=\"M9.5 3v3M14.5 3v3M9.5 18v3M14.5 18v3M3 9.5h3M3 14.5h3M18 9.5h3M18 14.5h3\"/>",
 "bracket": "<path d=\"M3 5h4v4H3M7 7h3.5M3 15h4v4H3M7 17h3.5M10.5 7v10M10.5 12h4\"/><circle cx=\"17.5\" cy=\"12\" r=\"2.6\"/>",
 "sigma": "<path d=\"M17.5 6.2V5H6.5l5.6 7-5.6 7h11v-1.2\"/>",
 "cpp": "<path d=\"M8.5 4.5c-1.7 0-2.5.8-2.5 2.5v2.3c0 1.4-.7 2.2-2 2.7 1.3.5 2 1.3 2 2.7V17c0 1.7.8 2.5 2.5 2.5M15.5 4.5c1.7 0 2.5.8 2.5 2.5v2.3c0 1.4.7 2.2 2 2.7-1.3.5-2 1.3-2 2.7V17c0 1.7-.8 2.5-2.5 2.5M12 9.8v4.4M9.8 12h4.4\"/>",
 "html": "<rect x=\"3\" y=\"4\" width=\"18\" height=\"16\" rx=\"2\"/><path d=\"M3 8.2h18M10 11.5l-2.5 2.3 2.5 2.3M14 11.5l2.5 2.3-2.5 2.3\"/>",
 "css": "<path d=\"M12 3a9 9 0 1 0 0 18c1.1 0 1.8-.8 1.8-1.8 0-.5-.2-.9-.5-1.2-.3-.3-.5-.7-.5-1.2 0-1 .8-1.8 1.8-1.8H17a4 4 0 0 0 4-4c0-4.4-4-8-9-8Z\"/><circle cx=\"7.6\" cy=\"11.6\" r=\".9\"/><circle cx=\"9.4\" cy=\"7.6\" r=\".9\"/><circle cx=\"14\" cy=\"7\" r=\".9\"/><circle cx=\"17\" cy=\"10.2\" r=\".9\"/>",
 "mysql": "<ellipse cx=\"12\" cy=\"6\" rx=\"8\" ry=\"3\"/><path d=\"M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3\"/>",
 "linux": "<rect x=\"3.5\" y=\"4\" width=\"17\" height=\"7\" rx=\"2\"/><rect x=\"3.5\" y=\"13\" width=\"17\" height=\"7\" rx=\"2\"/><path d=\"M7.5 7.5h.01M7.5 16.5h.01M11 7.5h5.5M11 16.5h5.5\"/>",
 "bash": "<path d=\"M14.6 7.6c-.5-1.2-1.6-1.9-3-1.9-1.8 0-3.1 1-3.1 2.5 0 3.4 6.4 1.9 6.4 5.3 0 1.6-1.4 2.7-3.3 2.7-1.5 0-2.8-.8-3.3-2.1M11.6 3.6v16.6M16.5 20h4\"/>",
 "git": "<circle cx=\"6.5\" cy=\"5.5\" r=\"2\"/><circle cx=\"6.5\" cy=\"18.5\" r=\"2\"/><circle cx=\"17.5\" cy=\"8\" r=\"2\"/><path d=\"M6.5 7.5v9M17.5 10v.8c0 2.6-1.7 3.9-4.6 4.3l-1.8.3c-2.2.3-3.6 1.1-4.3 2.1\"/>",
 "vscode": "<rect x=\"3\" y=\"4\" width=\"18\" height=\"16\" rx=\"2\"/><path d=\"M8 4v16M11 9h6M11 12.5h7M11 16h4\"/>",
 "pulse": "<path d=\"M3 12h3.5l2.5-6 4 12 2.5-6H21\"/>",
 "flame": "<g transform=\"translate(12 12) scale(1.22) translate(-12 -10.1)\"><path d=\"M12 3c.8 3.2 4.8 4.8 4.8 9.4a4.8 4.8 0 0 1-9.6 0c0-2.4 1.3-3.9 2.4-4.9.3 1.8 1.1 2.8 2.3 3.2C12 7.9 11.1 5.6 12 3Z\" stroke-width=\"1.23\"/></g>",
 "peak": "<path d=\"M3 19l5.5-8 3.5 4.5L15.5 9 21 19Z\"/><path d=\"M15.5 9V4.5l3 1.4-3 1.4\"/>",
 "folder": "<path d=\"M3 7a2 2 0 0 1 2-2h4l2 2.2h8a2 2 0 0 1 2 2V17a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z\"/>",
 "mail": "<rect x=\"3\" y=\"5\" width=\"18\" height=\"14\" rx=\"2\"/><path d=\"M3.5 6.5l8.5 6.5 8.5-6.5\"/>",
 "chat": "<path d=\"M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-7l-4.5 3.5V17H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z\"/><path d=\"M8 10.5h.01M12 10.5h.01M16 10.5h.01\"/>",
}


# ----------------------------------------------------------------- text ----

def mw(s, size, track=0):
    """Width of a monospace string (forced with textLength, so it is exact)."""
    return len(s) * 0.6 * size + max(len(s) - 1, 0) * track


def mono(x, y, s, size=14, fill=None, anchor='start', track=0, opacity=None, extra=''):
    fill = fill or C['cream']
    op = f' fill-opacity="{opacity}"' if opacity is not None else ''
    anc = '' if anchor == 'start' else f' text-anchor="{anchor}"'
    return (f'<text class="m" x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{op}{anc} '
            f'textLength="{mw(s, size, track):.1f}" lengthAdjust="spacing"{extra}>{escape(s)}</text>')


def serif(x, y, s, size, fill=None, anchor='start', italic=False, track=0, opacity=None):
    fill = fill or C['cream']
    it = ' font-style="italic"' if italic else ''
    ls = f' letter-spacing="{track}"' if track else ''
    op = f' fill-opacity="{opacity}"' if opacity is not None else ''
    anc = '' if anchor == 'start' else f' text-anchor="{anchor}"'
    return (f'<text class="s" x="{x:.1f}" y="{y:.1f}" font-size="{size}"{it}{ls} '
            f'fill="{fill}"{op}{anc}>{escape(s)}</text>')


def icon(name, x, y, size=40, color=None, sw=1.5):
    color = color or C['cream']
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({size / 24:.4f})" fill="none" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS[name]}</g>')

# ------------------------------------------------------------ document ----

class Doc:
    def __init__(self, h, title, desc, w=W):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.defs, self.body = [], []

    def d(self, s):
        self.defs.append(s)

    def b(self, s):
        self.body.append(s)

    def render(self, view=None):
        vx, vy, vw, vh = view or (0, 0, self.w, self.h)
        return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{vw}" height="{vh}" viewBox="{vx} {vy} {vw} {vh}" role="img" aria-labelledby="t d">'
                f'<title id="t">{escape(self.title)}</title><desc id="d">{escape(self.desc)}</desc>'
                f'<style>.m{{font-family:{MONO}}}.s{{font-family:{SERIF}}}</style>'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>\n')


def spline(n):
    return ';'.join(['.45 0 .55 1'] * n)

# All motion runs on two aligned clocks so that the browser repaints rarely:
# a slow 4 fps clock (breathing, drift, blink) and a 16 fps clock used only in
# short bursts (light sweeps). Every step lands on a multiple of 1/16 s.
SLOW, FAST = 4, 16


def stepped(attr, fn, dur, fps=SLOW, begin=0, fmt='{:.3f}', hold_until=None):
    """Discrete animation sampled at `fps`; fn(u) gives the value for u in [0, 1).
    If hold_until (0-1) is set, the motion happens before it and the value then rests."""
    n = int(round(dur * fps))
    span = n if hold_until is None else int(round(n * hold_until))
    vals, kts = [], []
    for i in range(span + 1):
        u = i / span
        vals.append(fmt.format(fn(min(u, 1.0))))
        kts.append(f'{(i / n) if i < span else span / n:.4f}')
    # remove consecutive duplicates (no repaint when nothing changes)
    v2, k2 = [vals[0]], [kts[0]]
    for v, k in zip(vals[1:], kts[1:]):
        if v != v2[-1]:
            v2.append(v); k2.append(k)
    return (f'<animate attributeName="{attr}" values="{";".join(v2)}" keyTimes="{";".join(k2)}" calcMode="discrete" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')


def stepped_tf(kind, fn, dur, fps=SLOW, begin=0, hold_until=None, additive=False):
    """Discrete animateTransform; fn(u) returns the transform values string."""
    n = int(round(dur * fps))
    span = n if hold_until is None else int(round(n * hold_until))
    vals, kts = [], []
    for i in range(span + 1):
        v = fn(min(i / span, 1.0))
        if vals and v == vals[-1]:
            continue
        vals.append(v)
        kts.append(f'{(i / n) if i < span else span / n:.4f}')
    add = ' additive="sum"' if additive else ''
    return (f'<animateTransform attributeName="transform" type="{kind}"{add} values="{";".join(vals)}" '
            f'keyTimes="{";".join(kts)}" calcMode="discrete" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')


def ease(u):
    return .5 - .5 * math.cos(math.pi * 2 * u)  # 0 -> 1 -> 0, smooth


def breathe(lo, hi, dur, begin=0):
    """Slow opacity breathing on the 4 fps clock (steps of under 1 %)."""
    begin = round(begin * 4) / 4
    return stepped('opacity', lambda u: lo + (hi - lo) * ease(u), dur, SLOW, begin, '{:.3f}')


def blink(dur=1.0):
    return (f'<animate attributeName="opacity" values="1;0" keyTimes="0;.5" calcMode="discrete" '
            f'dur="{dur}s" repeatCount="indefinite"/>')

# ---------------------------------------------------- window and atmosphere ----

def window_path(h, top=False, bottom=False, r=22, w=W):
    t = (f'M0 {r}Q0 0 {r} 0H{w - r}Q{w} 0 {w} {r}' if top else f'M0 0H{w}')
    bt = (f'V{h - r}Q{w} {h} {w - r} {h}H{r}Q0 {h} 0 {h - r}Z' if bottom else f'V{h}H0Z')
    return t + bt


def atmosphere(doc, seed, halos=(), flowers=(), bokeh=0, beam=None, top=False, bottom=False, extra=''):
    """Background shared by the section and by its frosted glass (via <use>)."""
    h = doc.h
    rnd = random.Random(seed)
    doc.d(f'<clipPath id="win"><path d="{window_path(h, top, bottom)}"/></clipPath>')
    doc.d('<radialGradient id="halo-c"><stop offset="0" stop-color="#F6E7CF" stop-opacity=".55"/>'
          '<stop offset=".45" stop-color="#E2C29A" stop-opacity=".16"/><stop offset="1" stop-color="#E2C29A" stop-opacity="0"/></radialGradient>')
    doc.d('<radialGradient id="halo-a"><stop offset="0" stop-color="#D9A877" stop-opacity=".42"/>'
          '<stop offset=".5" stop-color="#9C6B45" stop-opacity=".12"/><stop offset="1" stop-color="#9C6B45" stop-opacity="0"/></radialGradient>')
    doc.d('<radialGradient id="bokeh"><stop offset="0" stop-color="#FFF3DE" stop-opacity=".5"/>'
          '<stop offset=".6" stop-color="#F1E4CF" stop-opacity=".14"/><stop offset="1" stop-color="#F1E4CF" stop-opacity="0"/></radialGradient>')
    doc.d('<radialGradient id="floret"><stop offset="0" stop-color="#F8ECD8" stop-opacity=".95"/>'
          '<stop offset=".45" stop-color="#F1E4CF" stop-opacity=".45"/><stop offset="1" stop-color="#F1E4CF" stop-opacity="0"/></radialGradient>')
    doc.d('<radialGradient id="floret-r"><stop offset="0" stop-color="#C08A7F" stop-opacity=".9"/>'
          '<stop offset=".5" stop-color="#A5716A" stop-opacity=".4"/><stop offset="1" stop-color="#A5716A" stop-opacity="0"/></radialGradient>')
    doc.d('<linearGradient id="stem" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7A604A" stop-opacity=".3"/>'
          '<stop offset=".55" stop-color="#7A604A" stop-opacity=".06"/><stop offset="1" stop-color="#7A604A" stop-opacity="0"/></linearGradient>')
    doc.d('<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F6E7CF" stop-opacity="0"/>'
          '<stop offset=".5" stop-color="#F6E7CF" stop-opacity=".075"/><stop offset="1" stop-color="#F6E7CF" stop-opacity="0"/></linearGradient>')
    fade = min(.18, 46 / h)
    doc.d(f'<linearGradient id="edge" x1="0" y1="0" x2="0" y2="1">'
          f'<stop offset="0" stop-color="{C["bg"]}"/><stop offset="{fade:.3f}" stop-color="{C["bg"]}" stop-opacity="0"/>'
          f'<stop offset="{1 - fade:.3f}" stop-color="{C["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{C["bg"]}"/></linearGradient>')
    g = [f'<g id="atmo" clip-path="url(#win)"><rect width="{W}" height="{h}" fill="{C["bg"]}"/>']
    if beam:
        bx, bw, ang = beam
        g.append(f'<rect x="{bx}" y="{-h}" width="{bw}" height="{3 * h}" fill="url(#beam)" '
                 f'transform="rotate({ang} {bx + bw / 2} {h / 2})">{breathe(.55, 1, 13, 2)}</rect>')
    for i, (cx, cy, rx, ry, kind, lo, hi, dur) in enumerate(halos):
        g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#halo-{kind})">{breathe(lo, hi, dur, i * 1.5)}</ellipse>')
    for (cx, cy, sc, ang, n, op) in flowers:
        g.append(flower(rnd, cx, cy, sc, ang, int(n * .65), op * 1.1))
    for _ in range(min(bokeh, 4)):
        x, y, r = rnd.uniform(30, W - 30), rnd.uniform(40, h - 40), rnd.uniform(5, 16)
        g.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="url(#bokeh)" opacity="{rnd.uniform(.18, .45):.2f}"/>')
    g.append(extra)
    g.append(f'<rect width="{W}" height="{h}" fill="url(#edge)"/></g>')
    doc.b(''.join(g))


def flower(rnd, cx, cy, sc, ang, n, op):
    """Umbel of florets (yarrow-like). Motion blur is painted, not filtered:
    each floret is a soft gradient streak stretched along the wind direction."""
    parts = []
    stem_dx = rnd.uniform(-18, 18) * sc
    parts.append(f'<path d="M{cx:.0f} {cy + 10 * sc:.0f}Q{cx + stem_dx:.0f} {cy + 90 * sc:.0f} {cx + stem_dx * 1.6:.0f} {cy + 220 * sc:.0f}" '
                 f'stroke="url(#stem)" stroke-width="{3 * sc:.1f}" stroke-linecap="round" fill="none"/>')
    for _ in range(n):
        a = rnd.uniform(math.pi * 1.02, math.pi * 1.98)
        rr = math.sqrt(rnd.random())
        x = cx + math.cos(a) * 46 * sc * rr
        y = cy + math.sin(a) * 26 * sc * rr + 6 * sc
        r = rnd.uniform(3.2, 6.4) * sc
        grad = 'floret' if rnd.random() > .22 else 'floret-r'
        parts.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 3.2:.1f}" ry="{r * 1.05:.1f}" fill="url(#{grad})" '
                     f'opacity="{op * rnd.uniform(.45, 1):.2f}" transform="rotate({ang} {x:.1f} {y:.1f})"/>')
    return f'<g>{"".join(parts)}</g>'

# ------------------------------------------------------------- glass ----

def glass_defs(doc, sheen_dur=12, sheen_begin=1.5):
    doc.d('<linearGradient id="g-fill" x1="0" y1="0" x2="1" y2="1">'
          '<stop offset="0" stop-color="#FFFAF0" stop-opacity=".09"/><stop offset="1" stop-color="#FFFAF0" stop-opacity=".02"/></linearGradient>')
    doc.d('<linearGradient id="g-stroke" x1="0" y1="0" x2="1" y2="1">'
          '<stop offset="0" stop-color="#FFF8EB" stop-opacity=".35"/><stop offset="1" stop-color="#FFF8EB" stop-opacity=".05"/></linearGradient>')
    doc.d('<linearGradient id="g-spec" x1="0" y1="0" x2="1" y2="0">'
          '<stop offset="0" stop-color="#FFF8EB" stop-opacity="0"/><stop offset=".3" stop-color="#FFF8EB" stop-opacity=".42"/>'
          '<stop offset="1" stop-color="#FFF8EB" stop-opacity="0"/></linearGradient>')
    doc.d('<linearGradient id="g-wash" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#FFF8EB" stop-opacity=".07"/><stop offset="1" stop-color="#FFF8EB" stop-opacity="0"/></linearGradient>')
    doc.d('<filter id="noise" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" '
          'numOctaves="2" seed="11" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1 0 0 0 0 .97 0 0 0 0 .92 1 0 0 0 -.5"/></filter>')
    doc.d('<pattern id="grain" width="160" height="160" patternUnits="userSpaceOnUse">'
          '<rect width="160" height="160" filter="url(#noise)" opacity=".16"/></pattern>')
    # light sweep: a wide soft band glides across the glass in 6 s, then rests (12 s loop).
    # The band itself moves (rect x), the gradients stay still: moving a shape keeps repaints rare.
    doc.sheen = (sheen_dur, round(sheen_begin * 2) / 2)
    doc.d('<linearGradient id="band" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFF8EB" stop-opacity="0"/>'
          '<stop offset=".5" stop-color="#FFF8EB" stop-opacity=".12"/><stop offset="1" stop-color="#FFF8EB" stop-opacity="0"/></linearGradient>')
    doc.d('<linearGradient id="band-edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFF8EB" stop-opacity="0"/>'
          '<stop offset=".5" stop-color="#FFF8EB" stop-opacity=".75"/><stop offset="1" stop-color="#FFF8EB" stop-opacity="0"/></linearGradient>')


def sweep_band(doc, fill):
    dur, begin = doc.sheen
    h = doc.h
    move = stepped_tf('translate', lambda u: f'{2400 * (.5 - .5 * math.cos(math.pi * u)):.0f} 0', dur, FAST, begin, 5 / dur)
    return (f'<g transform="rotate(-24 500 {h / 2:.0f})"><rect x="-1100" y="{-600}" width="620" height="{h + 1200}" '
            f'fill="url(#{fill})">{move}</rect></g>')


def frost(doc, cards, blur=18):
    """Layer 1: the atmosphere re-drawn under the glass, blurred and clipped to the cards."""
    pad = blur * 3
    x0 = max(min(c[0] for c in cards) - pad, 0)
    y0 = max(min(c[1] for c in cards) - pad, 0)
    x1 = min(max(c[0] + c[2] for c in cards) + pad, W)
    y1 = min(max(c[1] + c[3] for c in cards) + pad, doc.h)
    doc.d(f'<filter id="frost" filterUnits="userSpaceOnUse" x="{x0:.0f}" y="{y0:.0f}" width="{x1 - x0:.0f}" height="{y1 - y0:.0f}" '
          f'color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{blur}"/>'
          '<feComponentTransfer><feFuncR type="linear" slope=".96" intercept=".006"/><feFuncG type="linear" slope=".95" intercept=".005"/>'
          '<feFuncB type="linear" slope=".93" intercept=".004"/></feComponentTransfer></filter>')
    rects = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>' for (x, y, w, h, r) in cards)
    doc.d(f'<clipPath id="cards">{rects}</clipPath>')
    doc.b('<g clip-path="url(#cards)"><use href="#atmo" xlink:href="#atmo" filter="url(#frost)"/></g>')


def glass(doc, cards):
    """Layers 2 to 5 of the frosted-glass cards (layer 1 comes from frost()).
    Shared layers (grain, surface sheen) are painted once through the cards clip."""
    fills, strokes, edges = [], [], []
    for (x, y, w, h, r) in cards:
        rr = f'x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"'
        wash_h = h * .42
        fills.append(f'<rect {rr} fill="url(#g-fill)"/>'
                     f'<path d="M{x} {y + r}Q{x} {y} {x + r} {y}H{x + w - r}Q{x + w} {y} {x + w} {y + r}V{y + wash_h:.0f}H{x}Z" fill="url(#g-wash)"/>'
                     f'<rect x="{x + r}" y="{y + .9}" width="{w - 2 * r}" height="1.1" fill="url(#g-spec)"/>')
        strokes.append(f'<rect {rr} fill="none" stroke="url(#g-stroke)" stroke-width="1.25"/>')
        edges.append(f'<rect {rr} fill="none" stroke="#fff" stroke-width="1.6"/>')
    doc.d(f'<mask id="edges" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{doc.h}">{"".join(edges)}</mask>')
    doc.b(''.join(fills) +
          f'<g clip-path="url(#cards)"><rect width="{W}" height="{doc.h}" fill="url(#grain)"/>{sweep_band(doc, "band")}</g>' +
          ''.join(strokes) + f'<g mask="url(#edges)">{sweep_band(doc, "band-edge")}</g>')


def frame(doc, top=False, bottom=False):
    """Window border, continuous from one stacked SVG to the next."""
    h = doc.h
    doc.d(f'<linearGradient id="frame" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{h}">'
          f'<stop offset="0" stop-color="#FFF8EB" stop-opacity="{.32 if top else .1}"/>'
          f'<stop offset="{min(1, 120 / h):.3f}" stop-color="#FFF8EB" stop-opacity=".1"/>'
          f'<stop offset="{max(0, 1 - 120 / h):.3f}" stop-color="#FFF8EB" stop-opacity=".1"/>'
          f'<stop offset="1" stop-color="#FFF8EB" stop-opacity="{.22 if bottom else .1}"/></linearGradient>')
    r, e = 22, .75
    if top:
        p = f'M{e} {h}V{r}Q{e} {e} {r} {e}H{W - r}Q{W - e} {e} {W - e} {r}V{h}'
    elif bottom:
        p = f'M{e} 0V{h - r}Q{e} {h - e} {r} {h - e}H{W - r}Q{W - e} {h - e} {W - e} {h - r}V0'
    else:
        p = f'M{e} 0V{h}M{W - e} 0V{h}'
    doc.b(f'<path d="{p}" fill="none" stroke="url(#frame)" stroke-width="1.5"/>')


def header(doc, y, num, title, caption=''):
    """Editorial section header: number, serif italic title, caption, hairline."""
    doc.d('<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C4A98B" stop-opacity=".5"/>'
          '<stop offset=".6" stop-color="#C4A98B" stop-opacity=".12"/><stop offset="1" stop-color="#C4A98B" stop-opacity="0"/></linearGradient>')
    out = mono(44, y, num, 13, C['sand'], track=2) + serif(78, y + 1, title, 27, C['cream'], italic=True)
    if caption:
        out += mono(956, y, caption, 12, C['umber'], anchor='end', track=1.5)
    out += f'<rect x="44" y="{y + 18}" width="912" height="1" fill="url(#rule)"/>'
    doc.b(out)

# ------------------------------------------------------------ signal panel ----

LEVELS = ('#1A1510', '#3B2B1D', '#62492F', '#9C7B5B', '#E2C9A6')
LANG = ('#F1E4CF', '#C4A98B', '#9C7B5B', '#A5716A', '#62492F', '#3A2C1F')


def levels(days):
    nz = sorted(c for c in days if c > 0)
    if not nz:
        return lambda c: 0
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)]
    return lambda c: 0 if c == 0 else (1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4)


def render_signal(data):
    doc = Doc(700, 'signal — live GitHub activity of ' + data['login'],
              f"{data['total']} contributions in the last year, current streak {data['current']} days, "
              f"longest streak {data['longest']} days, {data['repos']} public repositories.")
    atmosphere(doc, 5, halos=[(170, 250, 320, 170, 'c', .35, .8, 12), (860, 520, 330, 190, 'a', .3, .75, 14),
                              (520, 640, 260, 120, 'c', .2, .5, 10)],
               flowers=[(110, 520, 1.15, -18, 46, .55), (930, 200, 1.0, -22, 40, .45), (560, 120, .7, -15, 30, .3)],
               bokeh=10, beam=(620, 140, 24))
    glass_defs(doc, 12, 3)
    stats = [(40 + i * 233.33, 108, 220, 128, 16) for i in range(4)]
    langs = (40, 252, 920, 104, 18)
    field = (40, 372, 920, 252, 18)
    frost(doc, stats + [langs, field])
    header(doc, 64, '05', 'signal', 'live · ' + data['updated'])
    items = [('pulse', 'contributions', 'last 12 months', data['total'], ''),
             ('flame', 'current streak', 'days in a row', data['current'], 'd'),
             ('peak', 'longest streak', 'best run', data['longest'], 'd'),
             ('folder', 'public repos', 'on github', data['repos'], '')]
    glass(doc, stats + [langs, field])
    for (x, y, w, h, r), (ic, label, sub, val, unit) in zip(stats, items):
        doc.b(icon(ic, x + 20, y + 20, 26, C['sand']) +
              mono(x + 56, y + 31, label, 13, C['cream'], track=.5) +
              mono(x + 56, y + 49, sub, 11, C['umber'], track=.5) +
              serif(x + 22, y + 104, f'{val:,}'.replace(',', ' '), 46, C['cream']) +
              (mono(x + 30 + len(f'{val:,}') * 25, y + 104, unit, 14, C['sand']) if unit else ''))
    x, y, w, h, r = langs
    doc.b(mono(x + 24, y + 34, 'languages', 13, C['cream'], track=.5) +
          mono(x + w - 24, y + 34, 'public repos · by size', 11, C['umber'], anchor='end', track=.5))
    bx, bw = x + 24, w - 48
    doc.d(f'<clipPath id="bar"><rect x="{bx}" y="{y + 50}" width="{bw}" height="9" rx="4.5"/></clipPath>')
    cur, segs, legend = bx, [], []
    lx = bx
    for i, (name, pct) in enumerate(data['languages'][:6]):
        sw = bw * pct / 100
        segs.append(f'<rect x="{cur:.1f}" y="{y + 50}" width="{sw + .6:.1f}" height="9" fill="{LANG[i]}"/>')
        cur += sw
        lab = f'{name} {pct:.1f}%'.lower()
        legend.append(f'<circle cx="{lx + 4}" cy="{y + 80}" r="4" fill="{LANG[i]}"/>' + mono(lx + 14, y + 84.5, lab, 12, C['sand']))
        lx += 14 + mw(lab, 12) + 26
    doc.b(f'<g clip-path="url(#bar)">{"".join(segs)}</g>' + ''.join(legend))
    x, y, w, h, r = field
    weeks = data['weeks'][-53:]
    lvl = levels([c for wk in weeks for (_, c) in wk])
    cell, gap = 12, 4
    gx = x + (w - (len(weeks) * (cell + gap) - gap)) / 2
    gy = y + 72
    doc.b(mono(x + 24, y + 34, 'field of contributions', 13, C['cream'], track=.5) +
          mono(x + w - 24, y + 34, f"{data['total']} this year", 11, C['umber'], anchor='end', track=.5))
    cells, months, last_m, last_x = [], [], None, -99
    for i, wk in enumerate(weeks):
        for (wd, c) in wk:
            cells.append(f'<rect x="{gx + i * (cell + gap):.1f}" y="{gy + wd * (cell + gap)}" width="{cell}" height="{cell}" rx="3" fill="{LEVELS[lvl(c)]}"/>')
        m = data['week_months'][-53:][i]
        mx = gx + i * (cell + gap)
        if m != last_m and i < len(weeks) - 2 and (not months or mx - last_x > 34):
            months.append(mono(mx, gy - 12, m, 10, C['umber']))
            last_x = mx
        last_m = m
    lastw = len(weeks) - 1
    lwd = weeks[-1][-1][0]
    tx, ty = gx + lastw * (cell + gap) + cell / 2, gy + lwd * (cell + gap) + cell / 2
    doc.d(f'<radialGradient id="sweep"><stop offset="0" stop-color="#FFF3DE" stop-opacity=".34"/>'
          f'<stop offset="1" stop-color="#FFF3DE" stop-opacity="0"/></radialGradient>')
    doc.d(f'<clipPath id="grid"><rect x="{gx - 6:.0f}" y="{gy - 6}" width="{len(weeks) * (cell + gap) + 8:.0f}" height="{7 * (cell + gap) + 8}" rx="6"/></clipPath>')
    sx0, sx1 = gx - 170, gx + len(weeks) * (cell + gap) + 170
    sweep = (f'<g clip-path="url(#grid)"><ellipse cx="{sx0:.0f}" cy="{gy + 54}" rx="150" ry="95" fill="url(#sweep)">'
             + stepped_tf('translate', lambda u: f'{(sx1 - sx0) * (.5 - .5 * math.cos(math.pi * u)):.0f} 0', 16, FAST, 4, 7 / 16)
             + '</ellipse></g>')
    today = (f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="9.5" fill="none" stroke="#F1E4CF" stroke-width="1.2">'
             + breathe(.15, .85, 3) + '</circle>')
    lg = ''.join(f'<rect x="{x + w - 128 + i * 16}" y="{y + 214}" width="12" height="12" rx="3" fill="{LEVELS[i]}"/>' for i in range(5))
    doc.b(''.join(months) + ''.join(cells) + sweep + today +
          mono(x + w - 136, y + 224, 'less', 11, C['umber'], anchor='end') + lg + mono(x + w - 44, y + 224, 'more', 11, C['umber']) +
          mono(x + 24, y + 224, 'one square = one day', 11, C['umber'], track=.3))
    doc.b(mono(500, 668, 'generated by scripts/profile.py · refreshed every 12 h', 11, C['umber'], anchor='middle', track=1))
    frame(doc)
    return doc.render()

# ------------------------------------------------------------------- data ----

QUERY = """query($login:String!){ user(login:$login){
  repositories(first:100, ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC){ totalCount
    nodes{ languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } } }
  contributionsCollection{ contributionCalendar{ totalContributions
    weeks{ contributionDays{ date weekday contributionCount } } } } } }"""


def fetch(login, token):
    body = json.dumps({'query': QUERY, 'variables': {'login': login}}).encode()
    req = urllib.request.Request('https://api.github.com/graphql', data=body, headers={
        'Authorization': f'bearer {token}', 'Content-Type': 'application/json', 'User-Agent': 'itsnotjalan-profile'})
    with urllib.request.urlopen(req, timeout=40) as r:
        j = json.load(r)
    if j.get('errors'):
        raise SystemExit(f'GitHub API error: {j["errors"]}')
    u = j['data']['user']
    cal = u['contributionsCollection']['contributionCalendar']
    weeks = [[(d['weekday'], d['contributionCount'], d['date']) for d in wk['contributionDays']] for wk in cal['weeks']]
    sizes = {}
    for node in u['repositories']['nodes']:
        for e in node['languages']['edges']:
            sizes[e['node']['name']] = sizes.get(e['node']['name'], 0) + e['size']
    return summarize(login, cal['totalContributions'], weeks, u['repositories']['totalCount'], sizes)


def summarize(login, total, weeks, repos, sizes):
    days = [(d, c) for wk in weeks for (_, c, d) in wk]
    counts = [c for _, c in days]
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    cur = 0
    while i >= 0 and counts[i] > 0:
        cur, i = cur + 1, i - 1
    best = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        best = max(best, run)
    tot = sum(sizes.values()) or 1
    langs = sorted(((k, v * 100 / tot) for k, v in sizes.items()), key=lambda kv: -kv[1])
    if len(langs) > 6:
        langs = langs[:5] + [('other', sum(p for _, p in langs[5:]))]
    months = [datetime.date.fromisoformat(wk[0][2]).strftime('%b').lower() for wk in weeks]
    return {'login': login, 'total': total, 'current': cur, 'longest': best, 'repos': repos,
            'languages': langs, 'weeks': [[(wd, c) for (wd, c, _) in wk] for wk in weeks], 'week_months': months,
            'updated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M utc')}



# ============================================================ static panels ====

ASSETS = 'assets/'
PHOTO = None


def photo_b64():
    """The header photo, read once from assets/photo.jpg or from the old header.svg."""
    global PHOTO
    if PHOTO is None:
        import base64, re
        if os.path.exists(ASSETS + 'photo.jpg'):
            PHOTO = base64.b64encode(open(ASSETS + 'photo.jpg', 'rb').read()).decode()
        else:
            PHOTO = re.search(r'data:image/jpeg;base64,([A-Za-z0-9+/=]+)', open(ASSETS + 'header.svg').read()).group(1)
    return PHOTO


def save(name, text):
    open(ASSETS + name, 'w', encoding='utf-8').write(text)
    print(f'{name:22s} {len(text) / 1024:6.1f} KB')


# ------------------------------------------------------------------ hero ----

def typing(lines, x, y, size, step=.125, hold=2.5, gap=.5, lead=.5):
    """Rotating typed messages on the 10 fps clock: one character per 0.1 s,
    a pause, then the line clears at once. Reveal and caret use transforms only."""
    cw = .6 * size
    t, slots = lead, []
    for s in lines:
        n = len(s)
        a = t
        b = a + n * step
        c = b + hold
        slots.append((s, n, a, b, c))
        t = round((c + gap) * 8) / 8
    T = t
    k = lambda v: f'{v / T:.4f}'
    defs, body = [], []
    caret_kt, caret_v = ['0'], ['0 0']
    for i, (s, n, a, b, c) in enumerate(slots):
        full = n * cw
        kt, vals = ['0'], ['0 1']
        for j in range(1, n + 1):
            kt.append(k(a + j * step)); vals.append(f'{j / n:.4f} 1')
            caret_kt.append(k(a + j * step)); caret_v.append(f'{j * cw:.1f} 0')
        kt.append(k(c)); vals.append('0 1')
        caret_kt.append(k(c)); caret_v.append('0 0')
        defs.append(f'<clipPath id="ty{i}"><rect x="0" y="0" width="{full:.1f}" height="{size * 1.5:.0f}" '
                    f'transform="translate({x} {y - size})">'
                    f'<animateTransform attributeName="transform" type="scale" additive="sum" values="{";".join(vals)}" '
                    f'keyTimes="{";".join(kt)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></rect></clipPath>')
        body.append(f'<g clip-path="url(#ty{i})">{mono(x, y, s, size, C["cream"])}</g>')
        on0 = round(max(a - .25, 0) * 8) / 8
        body.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="0;{k(on0)};{k(c)}" calcMode="discrete" '
                    f'dur="{T}s" repeatCount="indefinite"/>{mono(934, y - 1, f"0{i + 1} / 0{len(lines)}", 11, C["umber"], anchor="end", track=1)}</g>')
    body.append(f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(caret_v)}" '
                f'keyTimes="{";".join(caret_kt)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/>'
                f'<rect x="{x + 2}" y="{y - size + 2}" width="9" height="{size + 3}" fill="{C["cream"]}">{blink()}</rect></g>')
    return ''.join(defs), ''.join(body)


def stepped_transform(kind, fn, dur, fps=4, additive=False):
    n = int(round(dur * fps))
    vals = [fn(i / n) for i in range(n)]
    kts = [f'{i / n:.4f}' for i in range(n)]
    add = ' additive="sum"' if additive else ''
    return (f'<animateTransform attributeName="transform" type="{kind}"{add} values="{";".join(vals)}" '
            f'keyTimes="{";".join(kts)}" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>')


def hero():
    doc = Doc(510, 'itsnotjalan — computer · ai · guitar · os · programming',
              'Profile header: motion-blurred flowers at dusk, name card and online status.')
    px, py, pw, ph = 20, 66, 960, 350
    doc.d(f'<clipPath id="photo"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="16"/></clipPath>')
    doc.d('<radialGradient id="sun"><stop offset="0" stop-color="#F6E7CF" stop-opacity=".5"/><stop offset="1" stop-color="#F6E7CF" stop-opacity="0"/></radialGradient>')
    doc.d('<linearGradient id="pf-l" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0B0907" stop-opacity=".72"/><stop offset=".55" stop-color="#0B0907" stop-opacity="0"/></linearGradient>')
    doc.d('<linearGradient id="pf-b" x1="0" y1="0" x2="0" y2="1"><stop offset=".45" stop-color="#0B0907" stop-opacity="0"/><stop offset="1" stop-color="#0B0907" stop-opacity=".88"/></linearGradient>')
    cx, cy = px + pw / 2, py + ph / 2
    zoom = stepped_transform('scale', lambda u: f'{1 + .05 * ease(u):.4f}', 90)
    drift = stepped_transform('translate', lambda u: f'{-12 * ease(u):.2f} {-5 * ease(u):.2f}', 90, additive=True)
    photo = (f'<g clip-path="url(#photo)"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#0B0907"/>'
             f'<g transform="translate({cx:.0f} {cy:.0f})"><g>{zoom}{drift}'
             f'<image x="{-pw / 2:.0f}" y="{-ph / 2:.0f}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMid slice" '
             f'href="data:image/jpeg;base64,{photo_b64()}"/></g></g>'
             f'<ellipse cx="250" cy="110" rx="330" ry="190" fill="url(#sun)">{breathe(.3, .8, 9)}</ellipse>'
             f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="url(#pf-l)"/>'
             f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="url(#pf-b)"/></g>'
             f'<rect x="{px + .5}" y="{py + .5}" width="{pw - 1}" height="{ph - 1}" rx="16" fill="none" stroke="#FFF8EB" stroke-opacity=".12"/>')
    atmosphere(doc, 1, top=True, extra=photo,
                   halos=[(820, 470, 300, 110, 'a', .35, .8, 13), (190, 480, 280, 110, 'c', .25, .6, 11)],
                   flowers=[(80, 520, .95, -18, 40, .4), (960, 440, .8, -20, 34, .32)], bokeh=5)
    glass_defs(doc, 12, 1)
    name_c = (40, 318, 548, 176, 20)
    pres_c = (608, 436, 352, 58, 16)
    frost(doc, [name_c, pres_c])
    glass(doc, [name_c, pres_c])
    doc.d('<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C4A98B" stop-opacity=".45"/>'
          '<stop offset=".6" stop-color="#C4A98B" stop-opacity=".12"/><stop offset="1" stop-color="#C4A98B" stop-opacity="0"/></linearGradient>')
    doc.b(f'<circle cx="36" cy="27" r="9" fill="none" stroke="{C["cream"]}" stroke-width="1">{breathe(.1, .55, 3)}</circle>'
          f'<circle cx="36" cy="27" r="4" fill="{C["cream"]}"/>' +
          mono(52, 31.5, 'itsnotjalan', 13, C['cream'], track=1) + mono(52 + mw('itsnotjalan', 13, 1) + 10, 31.5, '/ board', 13, C['umber'], track=1) +
          mono(968, 31.5, 'aix-en-provence · utc+1', 12, C['umber'], anchor='end', track=1) +
          '<rect x="20" y="51" width="960" height="1" fill="url(#rule)"/>')
    line = 'connected from aix-en-provence'
    lx = 74 + mw('> ', 14)
    doc.b(serif(70, 392, 'itsnotjalan', 54, C['cream'], track=8) +
          mono(74, 428, 'computer · ai · guitar · os · programming', 14, C['sand'], track=1.2) +
          mono(74, 466, '>', 14, C['sand']) + mono(lx, 466, line, 14, C['cream']) +
          f'<rect x="{lx + mw(line, 14) + 8:.1f}" y="454" width="9" height="16" fill="{C["cream"]}">{blink()}</rect>')
    doc.b(f'<circle cx="634" cy="465" r="9" fill="none" stroke="#B8CFA4" stroke-width="1">{breathe(.1, .6, 2)}</circle>'
          f'<circle cx="634" cy="465" r="4" fill="#B8CFA4"/>' +
          mono(648, 469.5, 'online', 13, C['cream'], track=.5) +
          mono(938, 469.5, 'semester 1 · iut aix', 12, C['sand'], anchor='end', track=.5))
    frame(doc, top=True)
    save('hero.svg', doc.render())


def status():
    doc = Doc(92, 'messages', 'Rotating messages: first-year computer science student; but informatique, iut aix-marseille; '
                              'learning how machines think; one command at a time.')
    atmosphere(doc, 9, halos=[(760, 46, 300, 60, 'a', .25, .55, 12), (200, 40, 240, 50, 'c', .15, .4, 10)], bokeh=2)
    glass_defs(doc, 12, 3)
    msg_c = (40, 12, 920, 64, 18)
    frost(doc, [msg_c])
    glass(doc, [msg_c])
    dd, bb = typing(['first-year computer science student', 'but informatique · iut aix-marseille',
                     'learning how machines think', 'one command at a time'], 140, 50.5, 17)
    doc.d(dd)
    doc.b(mono(66, 49, 'msg', 12, C['umber'], track=2) + '<rect x="112" y="30" width="1" height="28" fill="#FFF8EB" fill-opacity=".14"/>' + bb)
    frame(doc)
    save('status.svg', doc.render())


# ----------------------------------------------------------------- about ----

def about():
    doc = Doc(352, 'about itsnotjalan',
              'First-year computer science student, BUT Informatique, IUT Aix-Marseille, Aix-en-Provence. '
              'Learning how machines think, one command at a time. Off-screen: guitar, and whatever the light does at dusk.')
    atmosphere(doc, 2, halos=[(860, 120, 300, 150, 'c', .3, .7, 12), (120, 300, 280, 120, 'a', .25, .6, 14)],
                   flowers=[(950, 300, 1.0, -20, 40, 0.40), (60, 120, .8, -15, 30, 0.28)], bokeh=6, beam=(300, 120, 26))
    glass_defs(doc, 12, 2.4)
    c = (40, 104, 920, 220, 20)
    frost(doc, [c])
    glass(doc, [c])
    header(doc, 64, '01', 'about', 'board · thread #001')
    body = ['first-year computer science student — BUT Informatique,', 'IUT Aix-Marseille, Aix-en-Provence.',
            'learning how machines think, one command at a time.', 'off-screen: guitar, and whatever the light does at dusk.']
    out = (mono(68, 142, '[itsnotjalan]', 14, C['cream'], track=.5) + mono(68 + mw('[itsnotjalan]', 14, .5) + 12, 142, 'op', 11, C['umber'], track=1) +
           mono(932, 142, '2026/11/22 23:22', 12, C['umber'], anchor='end', track=1) +
           '<rect x="68" y="158" width="864" height="1" fill="url(#rule)"/>')
    for i, s in enumerate(body):
        out += mono(68, 194 + i * 28, s, 16, C['sand'])
    last = body[-1]
    out += f'<rect x="{68 + mw(last, 16) + 8:.1f}" y="{194 + 3 * 28 - 14}" width="9" height="18" fill="{C["cream"]}">{blink()}</rect>'
    out += mono(932, 306, 'reply below', 11, C['umber'], anchor='end', track=1.5)
    doc.b(out)
    frame(doc)
    save('about.svg', doc.render())

# ----------------------------------------------------------------- reply ----

def reply():
    doc = Doc(112, 'reply', 'Reply buttons: mail and discord.')
    atmosphere(doc, 3, halos=[(250, 60, 260, 70, 'a', .25, .55, 12), (750, 60, 260, 70, 'c', .2, .5, 12)], bokeh=3)
    glass_defs(doc, 10, .5)
    b1, b2 = (100, 22, 300, 58, 29), (600, 22, 300, 58, 29)
    frost(doc, [b1, b2])
    glass(doc, [b1, b2])
    for (x, y, w, h, r), ic, label in ((b1, 'mail', 'reply · mail'), (b2, 'chat', 'reply · discord')):
        doc.b(icon(ic, x + 26, y + 18, 22, C['sand']) + mono(x + 62, y + 34.5, label, 14, C['cream'], track=.5) +
              mono(x + w - 26, y + 34.5, '↗', 14, C['umber'], anchor='end'))
    frame(doc)
    full = doc.render()
    save('reply-mail.svg', doc.render((0, 0, 500, 112)).replace('aria-labelledby="t d"', 'aria-labelledby="t d"').replace('<title id="t">reply</title>', '<title id="t">reply via mail</title>'))
    save('reply-discord.svg', doc.render((500, 0, 500, 112)).replace('<title id="t">reply</title>', '<title id="t">reply via discord</title>'))

# ------------------------------------------------------- tiles sections ----

def interests():
    doc = Doc(300, 'interests', 'Frequencies: computer, ai, guitar, operating systems, programming.')
    atmosphere(doc, 4, halos=[(250, 180, 320, 120, 'c', .3, .7, 12), (800, 200, 300, 110, 'a', .25, .65, 15)],
                   flowers=[(520, 280, .9, -18, 36, 0.36), (40, 160, .7, -20, 26, 0.28)], bokeh=6)
    glass_defs(doc, 11, 3.5)
    w = (920 - 4 * 16) / 5
    tiles = [(40 + i * (w + 16), 104, round(w, 1), 160, 16) for i in range(5)]
    frost(doc, tiles)
    glass(doc, tiles)
    header(doc, 64, '02', 'frequencies', 'what keeps me up')
    for (x, y, tw, th, r), (ic, lab) in zip(tiles, [('computer', 'computer'), ('ai', 'ai'), ('guitar', 'guitar'),
                                                     ('os', 'operating systems'), ('code', 'programming')]):
        doc.b(icon(ic, x + tw / 2 - 23, y + 30, 46) + mono(x + tw / 2, y + 126, lab, 13.5, C['sand'], anchor='middle', track=.6))
    frame(doc)
    save('interests.svg', doc.render())


def learning():
    doc = Doc(380, 'currently learning',
              'Semester 1: web interfaces, databases and SQL, operating systems, computer architecture, algorithms, discrete maths.')
    atmosphere(doc, 6, halos=[(780, 160, 320, 140, 'c', .3, .7, 13), (200, 330, 300, 120, 'a', .25, .6, 11)],
                   flowers=[(70, 330, 1.0, -18, 40, 0.40), (930, 120, .75, -22, 30, 0.28)], bokeh=7, beam=(560, 120, 24))
    glass_defs(doc, 12, 1)
    w = (920 - 2 * 16) / 3
    tiles = [(40 + (i % 3) * (w + 16), 104 + (i // 3) * 128, round(w, 1), 112, 16) for i in range(6)]
    frost(doc, tiles)
    glass(doc, tiles)
    header(doc, 64, '03', 'currently learning', 'semester 1 · 2026')
    items = [('web', 'web interfaces', 'R1.02 · html · css'), ('db', 'databases & sql', 'R1.05 · mysql'),
             ('os', 'operating systems', 'R1.04 · linux · bash'), ('cpu', 'computer architecture', 'R1.03 · hardware'),
             ('bracket', 'algorithms', 'SAÉ 1.02 · tournaments'), ('sigma', 'discrete maths', 'R1.06 · logic · sets')]
    for (x, y, tw, th, r), (ic, title, sub) in zip(tiles, items):
        doc.b(icon(ic, x + 26, y + 38, 36) + mono(x + 82, y + 52, title, 15, C['cream']) + mono(x + 82, y + 76, sub, 12, C['umber'], track=.4))
    frame(doc)
    save('learning.svg', doc.render())


def toolbox():
    doc = Doc(284, 'toolbox', 'Tools used in class: c++, html, css, mysql, linux, bash, git, vs code.')
    atmosphere(doc, 7, halos=[(300, 200, 330, 110, 'a', .25, .6, 12), (820, 120, 300, 110, 'c', .25, .65, 14)],
                   flowers=[(960, 260, .9, -18, 34, 0.36), (420, 40, .6, -16, 24, 0.24)], bokeh=6)
    glass_defs(doc, 11, 2)
    w = (920 - 3 * 16) / 4
    chips = [(40 + (i % 4) * (w + 16), 104 + (i // 4) * 80, w, 64, 14) for i in range(8)]
    frost(doc, chips)
    glass(doc, chips)
    header(doc, 64, '04', 'toolbox', 'used in class')
    items = [('cpp', 'c++', 'R1.01'), ('html', 'html', 'R1.02'), ('css', 'css', 'R1.02'), ('mysql', 'mysql', 'R1.05'),
             ('linux', 'linux', 'R1.04'), ('bash', 'bash', 'R1.04'), ('git', 'git', 'versions'), ('vscode', 'vs code', 'editor')]
    for (x, y, tw, th, r), (ic, name, tag) in zip(chips, items):
        doc.b(icon(ic, x + 20, y + 19, 26) + mono(x + 60, y + 37.5, name, 15, C['cream'], track=.5) +
              mono(x + tw - 20, y + 37.5, tag, 11, C['umber'], anchor='end', track=.8))
    frame(doc)
    save('toolbox.svg', doc.render())

# ---------------------------------------------------------------- footer ----

def footer():
    doc = Doc(170, 'connection closed', 'End of the profile.')
    atmosphere(doc, 8, bottom=True, halos=[(500, 150, 360, 90, 'c', .25, .6, 12)],
                   flowers=[(70, 190, .8, -18, 30, 0.32), (940, 180, .7, -20, 26, 0.28)], bokeh=4)
    doc.d('<linearGradient id="fl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C4A98B" stop-opacity="0"/>'
          '<stop offset=".5" stop-color="#C4A98B" stop-opacity=".55"/><stop offset="1" stop-color="#C4A98B" stop-opacity="0"/></linearGradient>')
    doc.b(f'<rect x="180" y="40" width="640" height="1" fill="url(#fl)"/>'
          f'<g>{breathe(.45, 1, 6)}{mono(500, 84, "— connection closed —", 13, C["sand"], anchor="middle", track=5)}</g>' +
          mono(500, 114, 'itsnotjalan · aix-en-provence · 2026', 11, C['umber'], anchor='middle', track=2))
    frame(doc, bottom=True)
    save('footer.svg', doc.render())



STATIC = (hero, status, about, reply, interests, learning, toolbox, footer)


def main():
    args = sys.argv[1:]
    if '--data' in args:
        raw = json.load(open(args[args.index('--data') + 1]))
        data = summarize(raw['login'], raw['total'], raw['weeks'], raw['repos'], raw['sizes'])
        out = args[args.index('--out') + 1] if '--out' in args else 'dist/signal.svg'
    else:
        data, out = None, 'dist/signal.svg'
    for build in STATIC:
        build()
    if '--static' in args:
        return
    if data is None:
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            print('GITHUB_TOKEN not set: live panel skipped')
            return
        login = os.environ.get('PROFILE_LOGIN') or os.environ.get('GITHUB_REPOSITORY_OWNER')
        data = fetch(login, token)
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(render_signal(data))
    print(f'wrote {out}: {data["total"]} contributions, streak {data["current"]}/{data["longest"]}, {data["repos"]} repos')


if __name__ == '__main__':
    main()
