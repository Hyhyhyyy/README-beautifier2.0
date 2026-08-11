#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate sci-fi style README hero banners (1280x380) for the github-readme-beautify skill.

Art direction (per user request: "more sci-fi, like the very first style, plus particles
spread across the banner"):
  - Deep-space dark gradient background, per-repo neon accent (keeps each repo's identity)
  - Neon glow (feGaussianBlur merge) on the hero concept object
  - A PARTICLE FIELD (~60 particles) spread across the WHOLE 1280x380, each twinkling +
    gently drifting -> the requested "遍布横幅的粒子特效"
  - Diagonal light sweep beams (Rule 7a: travel >= 600px) + title draw-on underline
    (Rule 7b: anchor in title window)
  - Each repo gets a UNIQUE hand-drawn hero motif (no preset reuse -> Rule 6 passes)
  - Rule 3: hero life-animation lives in an INNER <g> (outer <g> only carries translate)
  - Rule 4: all motif shapes keep local coords within +/-260 of the (980,190) anchor

Output: banners/<name>.svg  (overwrites the Mascot versions; Mascot backups in _mascot/)
"""
import random, os

OUT = "C:/Users/lenovo/.workbuddy/skills/github-readme-beautify/banners"

# name -> (title, subtitle, tags, accent, accent2, bg1, bg2, motif_fn)
SPECS = [
    ("TOMATOMATOO", "双人习惯养成小程序", ["微信云开发", "番茄园"],
     "#ff4d6d", "#ffb38a", "#16070d", "#2c0e18", "tomato"),
    ("MyBlog", "纯静态 Markdown 博客", ["零云依赖", "marked"],
     "#34d399", "#6ee7b7", "#06140f", "#0c2a1e", "blog"),
    ("README-beautifier", "README 一键美化", ["横幅", "架构图", "徽章"],
     "#a855f7", "#f0abfc", "#0f0a1f", "#221043", "star"),
    ("Token_Saver", "Prompt 压缩与 Token 节省", ["语义缓存", "看板"],
     "#22d3ee", "#67e8f9", "#04141a", "#062a36", "coin"),
    ("train_guard", "LLM/VLM 训练守护", ["可靠性", "检查点"],
     "#3b82f6", "#93c5fd", "#060d1f", "#0c1f3d", "shield"),
    ("md-converter", "Markdown 互转", ["PDF", "DOCX", "纯前端"],
     "#38bdf8", "#7dd3fc", "#041426", "#082a4d", "doc"),
    ("KeLing1.0", "Android AI 学习助手", ["OCR", "知识点抽取"],
     "#f59e0b", "#fcd34d", "#1a1304", "#33260a", "viewfinder"),
    ("KeLing2.0", "知识卡片 · 跨端同步", ["Kotlin", "React"],
     "#fb7185", "#fecdd3", "#1a0a10", "#33121d", "card"),
    ("KeLing3.0", "多端知识管理", ["Monorepo", "轨道同步"],
     "#818cf8", "#c7d2fe", "#0a0a1f", "#1a1a40", "planet"),
    ("dlut-ultimate-website", "大工黑蚁极限飞盘队", ["飞盘", "官网"],
     "#84cc16", "#bef264", "#0f1a04", "#1f330a", "frisbee"),
    ("ChainPass", "去中心化身份", ["DID", "可验证凭证"],
     "#eab308", "#fde68a", "#14110a", "#2e2609", "key"),
    ("claude-code", "claude-code Python 移植", ["终端", "TS to Py"],
     "#f472b6", "#f9a8d4", "#1a0a14", "#331024", "terminal"),
]


def particles(seed, a, s, n=60):
    rnd = random.Random(seed)
    cols = ["#ffffff", a, s]
    out = []
    for _ in range(n):
        x = rnd.uniform(8, 1272)
        y = rnd.uniform(8, 372)
        r = rnd.uniform(0.6, 2.3)
        c = rnd.choice(cols)
        op = rnd.uniform(0.25, 0.9)
        dur = rnd.uniform(2.6, 6.5)
        beg = rnd.uniform(0, 5)
        dx = rnd.uniform(-5, 5)
        dy = rnd.uniform(-7, 7)
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c}" opacity="{op:.2f}">'
            f'<animate attributeName="opacity" values="{op:.2f};{op*0.3:.2f};{op:.2f}" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx:.1f} {dy:.1f};0 0" dur="{dur+4:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>'
            f'</circle>')
    return "".join(out)


def motif(name, a, s):
    """Return (shapes, anim) for the unique hero concept object, in local coords (~0,0)."""
    if name == "tomato":
        shapes = (
            '<circle cx="0" cy="0" r="104" fill="none" stroke="' + s + '" stroke-width="1" stroke-dasharray="3 7" opacity="0.55"/>'
            '<circle cx="0" cy="0" r="72" fill="' + a + '" fill-opacity="0.18" stroke="' + a + '" stroke-width="3"/>'
            '<ellipse cx="-22" cy="-26" rx="18" ry="11" fill="#ffffff" opacity="0.5"/>'
            '<path d="M0 -64 L13 -44 L34 -46 L21 -28 L33 -8 L0 -16 L-33 -8 L-21 -28 L-34 -46 L-13 -44 Z" fill="' + s + '" stroke="' + a + '" stroke-width="1.5"/>'
            '<rect x="-4" y="-80" width="8" height="20" rx="4" fill="' + s + '"/>'
            '<circle cx="104" cy="0" r="5" fill="' + s + '"/>'
            '<circle cx="-52" cy="92" r="3.5" fill="' + a + '"/>'
        )
        anim = ('<animateTransform attributeName="transform" type="rotate" values="-5 0 0;5 0 0;-5 0 0" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>'
                '<animateTransform attributeName="transform" type="scale" values="1 1;1.05 1.05;1 1" dur="5s" repeatCount="indefinite" additive="sum"/>')
    elif name == "blog":
        shapes = (
            '<rect x="-70" y="-82" width="96" height="124" rx="10" fill="#0c1a14" stroke="' + a + '" stroke-width="3"/>'
            '<rect x="-54" y="-60" width="64" height="6" rx="3" fill="' + s + '" opacity="0.75"/>'
            '<rect x="-54" y="-44" width="64" height="6" rx="3" fill="' + s + '" opacity="0.6"/>'
            '<rect x="-54" y="-28" width="44" height="6" rx="3" fill="' + s + '" opacity="0.6"/>'
            '<path d="M28 -74 L74 -28 L54 -8 L34 -28 Z" fill="' + s + '" stroke="' + a + '" stroke-width="2"/>'
            '<circle cx="54" cy="-8" r="4.5" fill="' + a + '"/>'
        )
        anim = ('<animateTransform attributeName="transform" type="translate" values="0 0;0 -10;0 0" dur="4s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    elif name == "star":
        shapes = (
            '<circle cx="0" cy="0" r="100" fill="none" stroke="' + s + '" stroke-width="1.5" stroke-dasharray="4 8" opacity="0.6"/>'
            '<path d="M0 -80 L18 -18 L80 0 L18 18 L0 80 L-18 18 L-80 0 L-18 -18 Z" fill="' + a + '" fill-opacity="0.22" stroke="' + a + '" stroke-width="3"/>'
            '<circle cx="0" cy="0" r="20" fill="' + s + '"/>'
            '<path d="M52 -52 l3 -8 3 8 8 3 -8 3 -3 8 -3 -8 -8 -3 z" fill="' + s + '"/>'
            '<path d="M-58 40 l2.5 -7 2.5 7 7 2.5 -7 2.5 -2.5 7 -2.5 -7 -7 -2.5 z" fill="' + a + '"/>'
        )
        anim = ('<animateTransform attributeName="transform" type="rotate" values="0 0 0;360 0 0" dur="20s" repeatCount="indefinite"/>'
                '<animateTransform attributeName="transform" type="scale" values="1 1;1.08 1.08;1 1" dur="3s" repeatCount="indefinite" additive="sum"/>')
    elif name == "coin":
        shapes = (
            '<polygon points="0,-72 62,-36 62,36 0,72 -62,36 -62,-36" fill="' + a + '" fill-opacity="0.18" stroke="' + a + '" stroke-width="3"/>'
            '<text x="0" y="16" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="58" font-weight="800" fill="' + s + '">$</text>'
            '<path d="M0 86 L0 116 M-13 103 L0 118 L13 103" stroke="' + s + '" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="-78" cy="-30" r="4" fill="' + a + '"/>'
            '<circle cx="80" cy="20" r="3.5" fill="' + s + '"/>'
        )
        anim = ('<animateTransform attributeName="transform" type="rotate" values="-10 0 0;10 0 0;-10 0 0" dur="4.2s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    elif name == "shield":
        shapes = (
            '<path d="M0 -92 L74 -66 L74 12 Q74 72 0 98 Q-74 72 -74 12 L-74 -66 Z" fill="' + a + '" fill-opacity="0.16" stroke="' + a + '" stroke-width="3"/>'
            '<polyline points="-52,2 -22,2 -10,-30 8,32 24,-14 42,2 54,2" fill="none" stroke="' + s + '" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
            '<path d="M40 -34 l16 16 M40 -18 l16 -16" stroke="' + s + '" stroke-width="4" fill="none" stroke-linecap="round"/>'
        )
        anim = ('<animateTransform attributeName="transform" type="scale" values="1 1;1.05 1.05;1 1" dur="3.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    elif name == "doc":
        shapes = (
            '<rect x="-98" y="-56" width="64" height="86" rx="8" fill="#0a1726" stroke="' + a + '" stroke-width="3"/>'
            '<rect x="-84" y="-42" width="36" height="6" rx="3" fill="' + s + '" opacity="0.7"/>'
            '<rect x="-84" y="-28" width="36" height="6" rx="3" fill="' + s + '" opacity="0.6"/>'
            '<rect x="-84" y="-14" width="24" height="6" rx="3" fill="' + s + '" opacity="0.6"/>'
            '<rect x="34" y="-56" width="64" height="86" rx="8" fill="#0a1726" stroke="' + s + '" stroke-width="3"/>'
            '<rect x="48" y="-42" width="36" height="6" rx="3" fill="' + a + '" opacity="0.7"/>'
            '<rect x="48" y="-28" width="36" height="6" rx="3" fill="' + a + '" opacity="0.6"/>'
            '<rect x="48" y="-14" width="24" height="6" rx="3" fill="' + a + '" opacity="0.6"/>'
            '<path d="M-18 0 L18 0 M6 -11 L20 0 L6 11 M-6 -11 L-20 0 L-6 11" stroke="' + s + '" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        anim = ('<animateTransform attributeName="transform" type="rotate" values="-7 0 0;7 0 0;-7 0 0" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    elif name == "viewfinder":
        shapes = (
            '<path d="M-82 -52 H-50 M-82 -52 V-20" stroke="' + a + '" stroke-width="4" fill="none" stroke-linecap="round"/>'
            '<path d="M82 -52 H50 M82 -52 V-20" stroke="' + a + '" stroke-width="4" fill="none" stroke-linecap="round"/>'
            '<path d="M-82 52 H-50 M-82 52 V20" stroke="' + a + '" stroke-width="4" fill="none" stroke-linecap="round"/>'
            '<path d="M82 52 H50 M82 52 V20" stroke="' + a + '" stroke-width="4" fill="none" stroke-linecap="round"/>'
            '<circle cx="0" cy="0" r="26" fill="none" stroke="' + s + '" stroke-width="2"/>'
            '<line x1="-12" y1="0" x2="12" y2="0" stroke="' + s + '" stroke-width="2"/>'
            '<line x1="0" y1="-12" x2="0" y2="12" stroke="' + s + '" stroke-width="2"/>'
            '<line x1="-82" y1="-52" x2="82" y2="-52" stroke="' + a + '" stroke-width="3"><animate attributeName="y1" values="-52;52;-52" dur="3s" repeatCount="indefinite"/><animate attributeName="y2" values="-52;52;-52" dur="3s" repeatCount="indefinite"/></line>'
        )
        anim = ('<animateTransform attributeName="transform" type="rotate" values="-4 0 0;4 0 0;-4 0 0" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    elif name == "card":
        shapes = (
            '<rect x="-30" y="-72" width="120" height="84" rx="12" fill="' + s + '" fill-opacity="0.15" stroke="' + s + '" stroke-width="2" transform="rotate(-9)"/>'
            '<rect x="-52" y="-52" width="120" height="84" rx="12" fill="#0c1a14" stroke="' + a + '" stroke-width="3"/>'
            '<rect x="-32" y="-32" width="24" height="16" rx="4" fill="' + a + '"/>'
            '<rect x="-32" y="-6" width="80" height="6" rx="3" fill="' + s + '" opacity="0.7"/>'
            '<rect x="-32" y="8" width="56" height="6" rx="3" fill="' + s + '" opacity="0.6"/>'
            '<circle cx="62" cy="-50" r="11" fill="' + s + '"/>'
        )
        anim = ('<animateTransform attributeName="transform" type="rotate" values="-12 0 0;12 0 0;-12 0 0" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    elif name == "planet":
        shapes = (
            '<circle cx="0" cy="0" r="64" fill="' + a + '" fill-opacity="0.2" stroke="' + a + '" stroke-width="3"/>'
            '<ellipse cx="-18" cy="-20" rx="22" ry="12" fill="#ffffff" opacity="0.35"/>'
            '<ellipse cx="0" cy="0" rx="106" ry="30" fill="none" stroke="' + s + '" stroke-width="2" transform="rotate(-18)"/>'
            '<g><animateTransform attributeName="transform" type="rotate" values="0 0 0;360 0 0" dur="8s" repeatCount="indefinite"/>'
            '<circle cx="106" cy="0" r="12" fill="' + s + '"/></g>'
        )
        anim = ('<animateTransform attributeName="transform" type="scale" values="1 1;1.05 1.05;1 1" dur="4s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    elif name == "frisbee":
        shapes = (
            '<path d="M-132 44 Q-186 12 -152 -32" stroke="' + s + '" stroke-width="3" fill="none" opacity="0.5" stroke-linecap="round"/>'
            '<ellipse cx="0" cy="0" rx="94" ry="40" fill="' + a + '" fill-opacity="0.18" stroke="' + a + '" stroke-width="3"/>'
            '<ellipse cx="0" cy="0" rx="94" ry="40" fill="none" stroke="' + s + '" stroke-width="1.5"/>'
            '<ellipse cx="0" cy="0" rx="36" ry="15" fill="none" stroke="' + s + '" stroke-width="2"/>'
        )
        anim = ('<animateTransform attributeName="transform" type="rotate" values="-10 0 0;10 0 0;-10 0 0" dur="4.4s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    elif name == "key":
        shapes = (
            '<circle cx="-42" cy="0" r="50" fill="none" stroke="' + s + '" stroke-width="1" stroke-dasharray="3 6" opacity="0.5"/>'
            '<circle cx="-42" cy="0" r="34" fill="none" stroke="' + a + '" stroke-width="6"/>'
            '<rect x="-8" y="-7" width="86" height="14" rx="7" fill="' + a + '"/>'
            '<rect x="50" y="7" width="13" height="24" rx="3" fill="' + s + '"/>'
            '<rect x="68" y="7" width="13" height="17" rx="3" fill="' + s + '"/>'
        )
        anim = ('<animateTransform attributeName="transform" type="rotate" values="-10 0 0;10 0 0;-10 0 0" dur="4.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    elif name == "terminal":
        shapes = (
            '<rect x="-88" y="-68" width="176" height="124" rx="14" fill="#0a0f1a" stroke="' + a + '" stroke-width="3"/>'
            '<circle cx="-68" cy="-52" r="5" fill="' + s + '"/>'
            '<circle cx="-52" cy="-52" r="5" fill="' + a + '"/>'
            '<circle cx="-36" cy="-52" r="5" fill="' + s + '"/>'
            '<rect x="-68" y="-36" width="70" height="7" rx="3" fill="' + a + '" opacity="0.8"/>'
            '<rect x="-68" y="-22" width="104" height="7" rx="3" fill="' + s + '" opacity="0.7"/>'
            '<rect x="-68" y="-8" width="48" height="7" rx="3" fill="' + a + '" opacity="0.8"/>'
            '<text x="-68" y="34" font-family="monospace" font-size="18" fill="' + a + '">$</text>'
            '<rect x="-50" y="22" width="10" height="16" fill="#ffffff"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>'
        )
        anim = ('<animateTransform attributeName="transform" type="translate" values="0 0;0 -8;0 0" dur="4s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>')
    else:
        shapes, anim = "", ""
    return shapes, anim


def title_layout(name):
    """Unified title sizing: cap fs=104 (~1.5x of the previous 70); long names auto-wrap
    to 2 lines so the text never overflows the ~776px left zone (hero starts ~x=848)."""
    fs = 104
    max_w = 720  # safe single-line width before the hero concept object
    est = len(name) * (fs * 0.5 - 1)
    if est <= max_w:
        ux2 = 72 + min(560, int(est))
        return fs, [name], [205], 250, ux2, ux2 - 72
    # wrap into 2 lines (prefer breaking at a hyphen for repo names)
    if '-' in name:
        parts = name.split('-')
        chosen = None
        for i in range(1, len(parts)):
            left = '-'.join(parts[:i]) + '-'
            right = '-'.join(parts[i:])
            if (len(left) * (fs * 0.5 - 1) <= max_w) and (len(right) * (fs * 0.5 - 1) <= max_w):
                chosen = (left, right); break
        if chosen is None:
            chosen = (parts[0] + '-', '-'.join(parts[1:]))
        line1, line2 = chosen
    else:
        mid = len(name) // 2
        line1, line2 = name[:mid], name[mid:]
    lh = int(fs * 1.02)
    y1, y2 = 138, 138 + lh
    lw = max(len(line1), len(line2)) * (fs * 0.5 - 1)
    ux2 = 72 + min(560, int(lw))
    return fs, [line1, line2], [y1, y2], y2 + 18, ux2, ux2 - 72


def build(spec):
    name, sub, tags, a, s, bg1, bg2, mkey = spec
    shapes, anim = motif(mkey, a, s)
    seed = abs(hash(name)) % (2 ** 31)
    part = particles(seed, a, s)
    # unified, enlarged title font-size (per user requests "统一调大" then "再放大两倍").
    # cap fs=104 (~1.5x of the previous 70); long names auto-wrap to 2 lines so the
    # text never overflows the ~776px left zone (hero concept object starts ~x=848).
    fs, lines, ylist, ul_y, ux2, L = title_layout(name)
    two = len(lines) == 2
    sub_y = 300 if two else 285
    tag_y = 312 if two else 300
    # pre-build multi-line title + draw-on underline (shared entrance animation)
    _ff = "'Segoe UI','Helvetica Neue',Arial,sans-serif"
    title_inner = "".join(
        f'<text x="72" y="{yy}" font-family="{_ff}" font-size="{fs}" font-weight="800" fill="url(#titleGrad)" letter-spacing="-1">{ln}</text>'
        for ln, yy in zip(lines, ylist))
    title_svg = (
        '<g>'
        '<animateTransform attributeName="transform" type="translate" values="-40 12;0 0;0 0" keyTimes="0;0.5;1" dur="1.6s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1;0 0 1 1"/>'
        '<animate attributeName="opacity" values="0;1;1" keyTimes="0;0.5;1" dur="1.6s" fill="freeze"/>'
        f'{title_inner}</g>')
    underline_svg = (
        f'<line x1="72" y1="{ul_y}" x2="{ux2}" y2="{ul_y}" stroke="url(#titleGrad)" stroke-width="4" stroke-linecap="round" stroke-dasharray="{L}" stroke-dashoffset="{L}">'
        '<animate attributeName="stroke-dashoffset" values="{L};0;0" keyTimes="0;0.55;1" dur="1.8s" fill="freeze"/>'
        '<animate attributeName="opacity" values="0;1;1" keyTimes="0;0.2;1" dur="1.8s" fill="freeze"/>'
        '</line>')
    tags_svg = ""
    tx = 74
    for t in tags[:3]:
        w = len(t) * 12 + 22
        tags_svg += (f'<rect x="{tx}" y="{tag_y}" width="{w}" height="24" rx="12" fill="{a}" fill-opacity="0.14" stroke="{a}" stroke-width="1"/>'
                    f'<text x="{tx + w / 2}" y="{tag_y + 16}" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="12" fill="{s}" opacity="0.9">{t}</text>')
        tx += w + 10

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 380" width="1280" height="380" role="img" aria-label="{name}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0" stop-color="{bg1}"/><stop offset="0.55" stop-color="{bg2}"/><stop offset="1" stop-color="{bg1}"/>
    </linearGradient>
    <linearGradient id="titleGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{s}"/>
    </linearGradient>
    <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{a}" stop-opacity="0"/><stop offset="0.5" stop-color="{a}" stop-opacity="0.9"/><stop offset="1" stop-color="{a}" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="vig" cx="0.5" cy="0.45" r="0.75">
      <stop offset="0.55" stop-color="#000000" stop-opacity="0"/><stop offset="1" stop-color="#000000" stop-opacity="0.55"/>
    </radialGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="blur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="40"/></filter>
  </defs>
  <rect width="1280" height="380" fill="url(#bg)"/>
  <g opacity="0.06" stroke="{a}" stroke-width="1">
    <line x1="0" y1="126" x2="1280" y2="126"/><line x1="0" y1="252" x2="1280" y2="252"/>
    <line x1="320" y1="0" x2="320" y2="380"/><line x1="640" y1="0" x2="640" y2="380"/><line x1="960" y1="0" x2="960" y2="380"/>
  </g>
  <g filter="url(#blur)" opacity="0.55">
    <circle cx="220" cy="120" r="150" fill="{a}"><animate attributeName="opacity" values="0.18;0.4;0.18" dur="9s" repeatCount="indefinite"/></circle>
    <circle cx="1090" cy="300" r="160" fill="{s}"><animate attributeName="opacity" values="0.15;0.38;0.15" dur="11s" repeatCount="indefinite"/></circle>
    <circle cx="980" cy="70" r="110" fill="{a}"><animate attributeName="opacity" values="0.12;0.3;0.12" dur="8s" repeatCount="indefinite"/></circle>
  </g>
  <g>{part}</g>
  <g transform="rotate(-18 640 190)" opacity="0.5">
    <rect x="-300" y="150" width="300" height="3" fill="url(#beam)"><animateTransform attributeName="transform" type="translate" values="-200 0;1700 0" dur="9s" repeatCount="indefinite"/></rect>
  </g>
  <g transform="rotate(-18 640 190)" opacity="0.32">
    <rect x="-260" y="250" width="220" height="2" fill="url(#beam)"><animateTransform attributeName="transform" type="translate" values="-200 0;1700 0" dur="13s" begin="2s" repeatCount="indefinite"/></rect>
  </g>
  <g transform="translate(980,190)"><g filter="url(#glow)">{anim}{shapes}</g></g>
  {underline_svg}
  {title_svg}
  <text x="74" y="{sub_y}" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="20" font-weight="500" fill="{s}">
    <animate attributeName="opacity" values="0;0;1" keyTimes="0;0.5;1" dur="1.8s" fill="freeze"/>
    {sub}
  </text>
  {tags_svg}
  <text x="1240" y="360" text-anchor="end" font-family="'Segoe UI',Arial,sans-serif" font-size="13" fill="{s}" opacity="0.5">made with &#10084; by Hyhyhyyy</text>
</svg>
'''


def main():
    for spec in SPECS:
        name = spec[0]
        svg = build(spec)
        path = os.path.join(OUT, name + ".svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", path, len(svg), "bytes")


if __name__ == "__main__":
    main()
