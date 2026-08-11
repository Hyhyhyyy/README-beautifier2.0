#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static QA validator for BESPOKE README banner SVGs (1280x380) AND badge URLs.

Context: every banner in this skill is hand-authored from a blank canvas. There is NO
shared motif/preset/THEMES library to reuse. The validator is the only shared tool, and
its job is purely defensive QA — it never supplies a shape. It catches the defect class
that produced the "ChainPass small blue dot" bug, the "train_guard 404 badge" bug, and
copy-reuse, WITHOUT a full SVG renderer:

  Rule 1  Well-formed XML (hard fail).
  Rule 2  Root viewBox must be exactly "0 0 1280 380" (hard fail).
  Rule 3  Anti-pattern: a group whose base transform is `translate(...)` must NOT
          have a direct-child <animateTransform type="rotate|scale"> (additive=replace
          wipes the translate, flinging the motif off-canvas — the blue-dot bug).
  Rule 4  Motif bounds: any right-side motif group (translate x in [900,1200]) must
          keep descendant shapes within a ~260px local box.
  Rule 5  Badge URL safety (README .md): shields.io static badge must resolve to
          2 segments (message-color) or 3 (label-message-color) after the '--' escape
          rule; wrong count → silent "404: badge not found" (HTTP 200 but broken).
  Rule 6  Uniqueness vs portfolio: a banner must NOT be structurally identical to
          (recolor-clone of) NOR share an identical motif group with any other banner
          in the baseline folder. This is the automated guard against accidental
          copying — it compares the new file against the existing `banners/` set.
  Rule 7  Mandatory motion layers (for NEW banners): every authored banner MUST have
          (a) a banner-wide motion — an animation whose horizontal travel/extent spans
          >= 600px across the canvas (a sweep beam, a full-width drifting field, or an
          animateMotion path crossing the width), AND (b) a title-surround motion — an
          animated element whose anchor sits in the title window (x <= 700, around the
          title text). This enforces the "motion across the whole banner + around the
          title" requirement. `--all` does NOT run Rule 7 (legacy baseline predates it);
          use `--motion` / `--gate` for newly authored banners.

Usage:
  python validate_banner.py banner.svg [more.svg ...]          # Rule 1-4 on each file
  python validate_banner.py --badges README.md [...]           # Rule 5 on .md files
  python validate_banner.py --check-unique <folder> [new.svg]  # Rule 6 across set
  python validate_banner.py --motion <file> [...]              # Rule 7 (two motion layers)
  python validate_banner.py --gate <folder> <new.svg>          # Rule 1-4 + 6 + 7 (pre-push)
  python validate_banner.py --all <folder> [new.svg]           # Rule 1-4 + Rule 6

  For Rule 6 / 7, pass the baseline folder (e.g. the skill's banners/) and a new file.
  Exit code 0 = all pass, 1 = at least one fail.
"""
import sys, os, re, xml.etree.ElementTree as ET

VIEW_W, VIEW_H = 1280, 380
MOTIF_X_MIN, MOTIF_X_MAX = 900, 1200
MOTIF_LOCAL_LIMIT = 260  # motif shapes must sit within +/- this of their anchor
MOTIF_SIG_MIN_LEN = 120  # ignore trivially small groups when matching motif shape


def ln(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def get_transform(el):
    return el.get("transform") or ""


def parse_numbers(s):
    return [float(x) for x in re.findall(r"-?\d+\.?\d*", s or "")]


def element_anchor(el):
    """Approximate anchor (x,y) of a graphical element from its as-written coords."""
    t = ln(el.tag)
    if t in ("circle", "ellipse"):
        return float(el.get("cx", "0")), float(el.get("cy", "0"))
    if t == "rect":
        return float(el.get("x", "0")), float(el.get("y", "0"))
    if t == "line":
        return float(el.get("x1", "0")), float(el.get("y1", "0"))
    if t == "text":
        return float(el.get("x", "0")), float(el.get("y", "0"))
    if t in ("polygon", "polyline"):
        pts = parse_numbers(el.get("points"))
        if len(pts) >= 2:
            xs, ys = pts[0::2], pts[1::2]
            return sum(xs) / len(xs), sum(ys) / len(ys)
    if t == "path":
        m = re.search(r"[Mm]\s*(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", el.get("d", ""))
        if m:
            return float(m.group(1)), float(m.group(2))
    return None


def validate_string(svg_text, name="<string>"):
    issues = []
    smil = svg_text.count("<animate")
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as e:
        return False, [f"Rule1 XML not well-formed: {e}"], smil, None

    # Rule 2: viewBox
    vb = root.get("viewBox", "")
    if vb.replace(",", " ") != "0 0 1280 380":
        issues.append(f"Rule2 viewBox '{vb}' != '0 0 1280 380'")

    def walk(el):
        nonlocal issues
        tr = get_transform(el)
        tr_match = re.search(r"translate\(\s*(-?\d+\.?\d*)[ ,]+(-?\d+\.?\d*)", tr)
        my_tx = float(tr_match.group(1)) if tr_match else 0.0
        my_ty = float(tr_match.group(2)) if tr_match else 0.0

        # Rule 3: translate-base group must not carry a direct rotate/scale animateTransform
        if tr_match:
            for child in list(el):
                if ln(child.tag) == "animateTransform":
                    ctype = (child.get("type") or "").lower()
                    if ctype in ("rotate", "scale"):
                        issues.append(
                            f"Rule3 {ln(el.tag)} has base translate AND direct "
                            f"animateTransform type='{ctype}' (additive=replace wipes translate)"
                        )

        # Rule 4: motif-group descendant bounds (as-written local coords)
        is_motif_anchor = tr_match and (MOTIF_X_MIN <= my_tx <= MOTIF_X_MAX)
        if is_motif_anchor:
            for desc in el.iter():
                if desc is el:
                    continue
                if re.search(r"translate\(", get_transform(desc) or ""):
                    continue  # nested translate handled on its own recursion
                a = element_anchor(desc)
                if a is None:
                    continue
                x, y = a
                if abs(x) > MOTIF_LOCAL_LIMIT or abs(y) > MOTIF_LOCAL_LIMIT:
                    issues.append(
                        f"Rule4 motif@{int(my_tx)},{int(my_ty)} child {ln(desc)} "
                        f"local ({x:.0f},{y:.0f}) exceeds +/-{MOTIF_LOCAL_LIMIT} "
                        f"(likely absolute coord inside translated group)"
                    )
        for child in list(el):
            walk(child)

    walk(root)
    return (len(issues) == 0), issues, smil, root


def validate_file(path):
    with open(path, "r", encoding="utf-8") as f:
        ok, issues, smil, _ = validate_string(f.read(), path)
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {os.path.basename(path)}  (SMIL={smil})")
    for i in issues:
        print(f"    - {i}")
    return ok


# ---------- Rule 5: Badge URL safety ----------
def split_shields_segments(bp):
    """Mimic shields.io static-badge parsing exactly.

    A single '-' is the label/message/color delimiter; a literal '--' is an escaped
    single '-' inside a field. Reproducing this is what lets us agree with what
    shields.io actually renders (root cause of the silent 404 "badge not found").
    """
    segments, cur, i = [], [], 0
    while i < len(bp):
        if bp[i] == "-" and i + 1 < len(bp) and bp[i + 1] == "-":
            cur.append("-"); i += 2
        elif bp[i] == "-":
            segments.append("".join(cur)); cur = []; i += 1
        else:
            cur.append(bp[i]); i += 1
    segments.append("".join(cur))
    return segments


def validate_badges_in_md(md_text):
    issues = []
    urls = re.findall(r'!\[.*?\]\((https://img\.shields\.io/badge/[^)]+)\)', md_text)
    for u in urls:
        m = re.match(r'.*/badge/([^?]+)', u)
        if not m:
            continue
        bp = m.group(1)
        segs = split_shields_segments(bp)
        if len(segs) < 2 or len(segs) > 3:
            issues.append(f"Rule5 badge resolves to {len(segs)} segments (need 2 or 3): '{bp[:80]}' → 404")
        if any(s == "" for s in segs):
            issues.append(f"Rule5b badge has empty segment: '{bp[:80]}' → 404")
    return len(issues) == 0, issues


def validate_badge_file(path):
    with open(path, "r", encoding="utf-8") as f:
        md_text = f.read()
    ok, issues = validate_badges_in_md(md_text)
    status = "PASS" if ok else "FAIL"
    n = len(re.findall(r'!\[.*?\]\(https?://[^)]+\)', md_text))
    print(f"[{status}] {os.path.basename(path)}  ({n} badges)")
    for i in issues:
        print(f"    - {i}")
    return ok


# ---------- Rule 6: Uniqueness vs portfolio (no copy-reuse) ----------
def _norm_text(s):
    """Strip colors + ids + whitespace → structural fingerprint."""
    s = re.sub(r"#[0-9a-fA-F]{3,8}", "C", s)
    s = re.sub(r'id="[^"]+"', "id", s)
    return re.sub(r"\s+", "", s)


def _motif_signatures(root):
    """Return normalized shape-strings of every right-side hero motif group.

    Strips the translate anchor + colors + ids so two banners that draw the SAME
    object (even at different positions / hues) yield identical signature strings.
    Only meaningful (non-trivial) groups are returned.
    """
    sigs = []
    for el in root.iter():
        if ln(el.tag) != "g":
            continue
        tr = get_transform(el)
        m = re.search(r"translate\(\s*(-?\d+\.?\d*)[ ,]+(-?\d+\.?\d*)", tr)
        if not m or not (MOTIF_X_MIN <= float(m.group(1)) <= MOTIF_X_MAX):
            continue
        s = ET.tostring(el, encoding="unicode")
        s = re.sub(r'id="[^"]+"', "id", s)
        s = re.sub(r"#[0-9a-fA-F]{3,8}", "C", s)
        s = re.sub(r'transform="translate\([^)]*\)"', "", s)  # ignore anchor position
        s = re.sub(r"\s+", "", s)
        if len(s) >= MOTIF_SIG_MIN_LEN:
            sigs.append(s)
    return sigs


def collect_svgs(args):
    """Expand dirs → *.svg; keep explicit .svg paths. Returns ordered unique list."""
    paths = []
    for a in args:
        if os.path.isdir(a):
            for f in sorted(os.listdir(a)):
                if f.endswith(".svg"):
                    paths.append(os.path.join(a, f))
        elif a.endswith(".svg") and os.path.exists(a):
            paths.append(a)
    # de-dup, preserve order
    seen, out = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p); out.append(p)
    return out


def uniqueness_report(paths, verbose=True):
    """Rule 6: compare every banner in `paths` against every other.

    FAIL if (a) two banners are structurally identical (recolor clone) or
            (b) two banners share an identical hero-motif shape (reused object).
    Returns True only if zero collisions.
    """
    records = []  # (path, full_norm, [motif_sigs])
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                txt = f.read()
        except Exception as e:
            if verbose:
                print(f"  [ERR ] {os.path.basename(p)}: {e}")
            return False
        try:
            _, _, _, root = validate_string(txt, p)
        except Exception:
            root = None
        if root is None:
            if verbose:
                print(f"  [ERR ] {os.path.basename(p)}: not parseable")
            return False
        records.append((p, _norm_text(txt), _motif_signatures(root)))

    collisions = []
    # (a) full structural equality → recolor clone
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            if records[i][1] == records[j][1]:
                collisions.append(
                    f"recolor-clone (structurally identical): "
                    f"{os.path.basename(records[i][0])} == {os.path.basename(records[j][0])}"
                )
    # (b) shared hero-motif shape
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            shared = set(records[i][2]) & set(records[j][2])
            if shared:
                collisions.append(
                    f"reused motif shape: {os.path.basename(records[i][0])} ~ "
                    f"{os.path.basename(records[j][0])} (identical hero object)"
                )

    if verbose:
        print(f"Compared {len(records)} banner(s):")
        for p, fn, sigs in records:
            print(f"  {os.path.basename(p):28} motif-shapes={len(sigs)}")
        if collisions:
            print("\n[FAIL] Uniqueness collisions found:")
            for c in collisions:
                print(f"  - {c}")
        else:
            print("\n[PASS] No recolor-clones and no reused motif shapes.")
    return len(collisions) == 0


# ---------- Rule 7: mandatory motion layers (new banners) ----------
def _anchor_x_of(el, parent_map):
    """Approximate x position of an element: translate-x of nearest ancestor g,
    else its own x/cx (so an animated child is attributed to its group center)."""
    cur = el
    while cur is not None:
        m = re.search(r"translate\(\s*(-?\d+\.?\d*)[ ,]+(-?\d+\.?\d*)", get_transform(cur))
        if m:
            return float(m.group(1))
        a = element_anchor(cur)
        if a is not None:
            return a[0]
        cur = parent_map.get(cur)
    return None


def check_motion(svg_text, verbose=True):
    """Rule 7: a new banner MUST have BOTH:
      (a) banner-wide motion  — an animation spanning >= 600px horizontally, OR a
          full-width shape (width>=1000) that is itself animated.
      (b) title-surround motion — an animated element whose anchor sits in the title
          window (around the title <text>, x <= 700).
    Returns (ok, banner_wide, title_motion)."""
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as e:
        if verbose:
            print(f"  [ERR] not parseable: {e}")
        return False, False, False

    title_x = 200.0
    for el in root.iter():
        if ln(el.tag) == "text" and el.get("x"):
            try:
                title_x = float(el.get("x")); break
            except ValueError:
                pass
    win_lo, win_hi = title_x - 320, title_x + 540

    parent_map = {c: p for p in root.iter() for c in p}
    banner_wide = False
    title_motion = False
    reasons = []

    for anim in root.iter():
        t = ln(anim.tag)
        if t not in ("animate", "animateTransform", "animateMotion"):
            continue
        ax = _anchor_x_of(parent_map.get(anim), parent_map)
        if t == "animateTransform":
            mtype = (anim.get("type") or "").lower()
            if mtype == "translate":
                nums = parse_numbers(anim.get("values") or "")
                xs = nums[0::2]
                rng = (max(xs) - min(xs)) if len(xs) >= 2 else 0
                if rng >= 600:
                    banner_wide = True; reasons.append("wide translate sweep")
                    continue
            if ax is not None and win_lo <= ax <= win_hi:
                title_motion = True
        elif t == "animateMotion":
            nums = parse_numbers(anim.get("path") or "")
            xs = nums[0::2]
            rng = (max(xs) - min(xs)) if len(xs) >= 2 else 0
            if rng >= 600:
                banner_wide = True; reasons.append("wide animateMotion path")
                continue
            if ax is not None and win_lo <= ax <= win_hi:
                title_motion = True
        else:  # animate
            attr = (anim.get("attributeName") or "").lower()
            if attr == "x":
                nums = parse_numbers(
                    (anim.get("values") or "") + " "
                    + (anim.get("from") or "") + " " + (anim.get("to") or "")
                )
                rng = (max(nums) - min(nums)) if len(nums) >= 2 else 0
                if rng >= 600:
                    banner_wide = True; reasons.append("wide x sweep")
                    continue
            if ax is not None and win_lo <= ax <= win_hi:
                title_motion = True

    for el in root.iter():
        if ln(el.tag) == "rect":
            try:
                w = float(el.get("width", "0"))
            except ValueError:
                w = 0
            if w >= 1000:
                for c in list(el):
                    if ln(c.tag) == "animate" and (c.get("attributeName") in
                                                   ("x", "opacity", "stroke-dashoffset")):
                        banner_wide = True; reasons.append("full-width shape animated")

    ok = banner_wide and title_motion
    if verbose:
        print(f"  banner-wide motion   : {'YES' if banner_wide else 'NO'}")
        print(f"  title-surround motion: {'YES' if title_motion else 'NO'}")
        if reasons:
            print(f"  (detected: {', '.join(reasons)})")
        print(f"  [{'PASS' if ok else 'FAIL'}] Rule 7 motion layers")
    return ok, banner_wide, title_motion


def validate_folder(args):
    """Rule 1-4 on each svg found in args + Rule 6 across them. Returns ok."""
    paths = collect_svgs(args)
    if not paths:
        print("[SKIP] no .svg files found in the given path(s)")
        return False
    ok = True
    print(f"Validating {len(paths)} banner(s) (Rule 1-4)...\n")
    for p in paths:
        ok = validate_file(p) and ok
    print()
    ok = uniqueness_report(paths, verbose=True) and ok
    return ok


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    if args[0] == "--badges":
        ok = True
        for p in args[1:]:
            if not os.path.exists(p):
                print(f"[SKIP] {p} (not found)"); ok = False; continue
            ok = validate_badge_file(p) and ok if p.endswith(".md") else ok
            if not p.endswith(".md"):
                print(f"[SKIP] {p} (not .md)")
        return 0 if ok else 1
    if args[0] == "--check-unique":
        paths = collect_svgs(args[1:])
        if not paths:
            print("[SKIP] no .svg files found in the given path(s)")
            return 1
        return 0 if uniqueness_report(paths, verbose=True) else 1
    if args[0] == "--motion":
        ok = True
        for p in args[1:]:
            if not os.path.exists(p):
                print(f"[SKIP] {p} (not found)"); ok = False; continue
            with open(p, "r", encoding="utf-8") as f:
                txt = f.read()
            print(f"[Rule7] {os.path.basename(p)}")
            mok, _, _ = check_motion(txt, verbose=True)
            ok = ok and mok
        return 0 if ok else 1
    if args[0] == "--gate":
        folder = args[1] if len(args) > 1 else "."
        newfiles = []
        for a in args[2:]:
            if not a.endswith(".svg"):
                continue
            if os.path.exists(a):
                newfiles.append(a)
            else:
                cand = os.path.join(folder, a)
                newfiles.append(cand if os.path.exists(cand) else a)
        paths = collect_svgs([folder]) + newfiles
        seen, allp = set(), []
        for p in paths:
            if p not in seen:
                seen.add(p); allp.append(p)
        ok = True
        print("=== Rule 1-4 ===")
        for p in allp:
            ok = validate_file(p) and ok
        print("\n=== Rule 6 uniqueness ===")
        ok = uniqueness_report(allp, verbose=True) and ok
        print("\n=== Rule 7 motion (new file) ===")
        if newfiles:
            for nf in newfiles:
                with open(nf, "r", encoding="utf-8") as f:
                    txt = f.read()
                print(f"[Rule7] {os.path.basename(nf)}")
                mok, _, _ = check_motion(txt, verbose=True)
                ok = ok and mok
        else:
            print("[SKIP] --gate needs a new .svg file to motion-check; passed Rule 7")
        return 0 if ok else 1
    if args[0] == "--all":
        return 0 if validate_folder(args[1:]) else 1
    # default: positional files (.md → badges, else SVG Rule1-4)
    ok = True
    for p in args:
        if not os.path.exists(p):
            print(f"[SKIP] {p} (not found)"); ok = False; continue
        if p.endswith(".md"):
            ok = validate_badge_file(p) and ok
        else:
            ok = validate_file(p) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
