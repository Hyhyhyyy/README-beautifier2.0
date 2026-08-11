# github-readme-beautify

Reusable **WorkBuddy skill**: beautify one or more GitHub repository READMEs with an
animated hero banner — a standalone SVG using **SMIL animation** that plays inline in
GitHub (no `<style>`/`<script>`, which GitHub strips from READMEs).

## Install

Copy (or symlink) this folder into your WorkBuddy skills directory:

```bash
# user-level (all projects)
cp -r github-readme-beautify ~/.workbuddy/skills/

# or project-level
cp -r github-readme-beautify <your-project>/.workbuddy/skills/
```

Then invoke the skill (`github-readme-beautify`) in a WorkBuddy conversation.

## What it produces

- `banner.svg` (1280×380) — a hand-drawn, animated hero banner you reference at the
  top of the target repo's README: `![banner](banner.svg)`
- Enhanced README (optional) — top banner + safe shields.io badges + original content.

## Visual style (current default: Mascot / core-concept)

- **Multi-color**: ≥3-stop background gradient + 2–3 accent colors.
- **No round frame** around the mascot.
- **A single animated mascot / core-concept object** with a life animation
  (bob / scale pulse / rotate / swing) — kept in an *inner* `<g>` so the outer
  `<g>` only carries the base `translate()` (avoids transform-wipe Rule 3).
- **Lots of whitespace**, soft non-ring `radialGradient` glow behind the hero.

### Two mandatory motion layers (Rule 7)

1. **Banner-wide sweep** — an animation whose horizontal travel ≥ 600px
   (e.g. a light beam `<rect x="-220 ... ">` animating `x` `-220 → 1300 → -220`).
2. **Title-surround motion** — a draw-on underline (`stroke-dashoffset`) or glow
   pulse anchored inside the title window.

## Workflow

1. Read the full target README (description + topics) — design from *what the
   project actually does*, never the literal repo name.
2. Hand-draw a fresh `banner.svg` on a blank 1280×380 canvas. **No preset reuse** —
   each banner gets a unique signature object + unique animation + fresh palette.
3. Validate before pushing:

   ```bash
   python scripts/validate_banner.py --gate banners/ banner.svg   # Rule 1-4 + 6 + 7
   python scripts/validate_banner.py --all  banners/               # Rule 1-4 + 6 (uniqueness)
   ```

   - **Rule 6 (uniqueness gate)**: compared against the `banners/` baseline — a
     color-swapped clone or a copied motif → FAIL.
   - **Rule 3 (transform-wipe)**: never put a `rotate`/`scale` `<animateTransform>`
     on the same `<g>` that has a base `translate()`; nest an inner `<g>`.

4. Push reliably via `git clone → overwrite root banner.svg → commit → push`
   (the `gh api` PUT path is unreliable for some repos).

## Repo layout

```
SKILL.md              # skill definition (read by WorkBuddy)
scripts/validate_banner.py   # static QA checker (Rule 1-4, 6, 7)
references/principles.md     # hand-drawn design principles
assets/sample-banner.svg     # single Mascot-style example
banners/              # 12 delivered banner examples (uniqueness baseline + _legacy)
```

## Examples (in banners/)

TOMATOMATOO (tomato), MyBlog (pen nib), README-beautifier (pulsing star),
Token_Saver (coin), train_guard (shield), md-converter (doc), KeLing1.0/2.0/3.0
(viewfinder / card / planet), dlut-ultimate-website (frisbee), ChainPass (key),
claude-code (terminal).
