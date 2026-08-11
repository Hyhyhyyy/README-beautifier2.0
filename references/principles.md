# Banner Design Principles (bespoke authoring)

This skill deliberately has **no motif library, no animation-preset dictionary, no
THEMES data file, and no shared palette presets**. Every banner is hand-authored from
a blank canvas for the one repo it belongs to. The only shared tool is the QA validator
(`scripts/validate_banner.py`), which checks technical correctness and guards against
accidental copying — it never suggests or supplies a shape to reuse.

Why: a preset library makes "change the color and reuse the SVG" far too easy, and that
reads as templated. Ground-up authoring is the only way to guarantee a portfolio that
looks like a *family of distinct crafts*, not a *template with swapped hues*.

## Read everything first (content → concept, never the title)

The single biggest failure mode is designing from the *name*. "ChainPass" does not
mean "a chain and a password" — its README says it is a *W3C DID + verifiable-credential
+ cross-border-payment + KYC-compliance + ZKP-login* platform. Design from what the
project **does**, not what its title sounds like.

1. **Read the FULL README** (+ `description` + `topics`). Capture: what it is, core
   features, tech stack, audience/vibe.
2. **Synthesize 2–3 visual concepts from the content.** E.g. for ChainPass the strongest
   concept is *"a self-sovereign verifiable-credential that is cryptographically verified,
   then flows across a decentralized identity network and across borders into compliant
   payment"* — that single sentence fuses DID + VC + payment + compliance.
3. **Pick the concept that represents the whole**, and write a one-line rationale
   (keeps the next authoring run honest). If you reach for the name's literal object,
   stop and re-read the features list.

## Two mandatory motion layers (on EVERY banner)

A banner is not finished with only the hero object's animation. Every banner MUST have:

1. **Banner-wide motion** — an animation that exists across the *entire* 1280px width.
   Techniques: a light beam sweeping left→right (`<rect>` with `<animate>` on `x` from
   −140 → 1420), a particle field drifting across, or a gradient wash. Its travel/extent
   must span ≥ 600px horizontally so it visibly crosses the whole canvas.
   *Purpose: unify the composition; give the whole banner life, not just the corner.*
2. **Title-surround motion** — animation localized *around the title text* (left zone,
   x ≤ 700). Techniques: orbiting accent dots (a `<g>` at the title center with a child
   `<animateTransform type="rotate">`), a pulsing halo behind the title (`<circle>`
   animating `r`/`opacity`), an underline that draws in (`<line>` with `stroke-dashoffset`
   animation), or particles rising from the letters.
   *Purpose: pull the eye to the project name.*

These two layers are checked by Rule 7 in `validate_banner.py` — a new banner that
misses either one FAILS the gate.

## Mascot / core-concept visual language (bold, colorful, alive)

The standing art direction: every banner centers on a **lively mascot or core-concept object
that MOVES**, drawn boldly in **rich, multi-color** palettes. Non-negotiables:

1. **Bold strokes.** Emblems use `stroke-width` in the **6–12** range — not hairlines. Thick
   contours make the mascot read as a confident mark.
2. **Rich, multi-color palettes (≥ 3 colors).** Use vibrant **multi-stop gradients** (blend
   2–3 hues) for the background AND **2–3 accent colors** on the mascot. Colorful and diverse —
   not a single deep base + one accent. (Keep title text contrast readable.)
3. **Animated mascot / core concept object — the hero moves.** The central object is ALIVE:
   bob/float (`<animateTransform type="translate">` on an *inner* `<g>`), gentle rotate, swing,
   pulse/scale, or a moving sub-part. It should read as a *character* or *key concept in motion*,
   not a static logo. Nest the motion in an inner `<g>` — never on the same `<g>` as the base
   `translate()` (transform-wipe rule).
4. **NO circular badge frame.** Do NOT box the mascot in a ring/circle. Let it breathe freely
   in open space. A *soft, non-ring* backdrop (faint blob, scattered dots, or gradient glow) is
   allowed for depth — but never a containing circle.
5. **One focal concept, not a pile.** One strong mascot/object + minimal support (soft backdrop
   + title). No element stacking (coins + satellites + cards + arrows at once). If a 3rd discrete
   object appears, cut it.
6. **Generous negative space (大气).** Surround the mascot with empty canvas.
7. **Keep BOTH mandatory motion layers (Rule 7):** a banner-wide sweep (≥ 600px) *behind* the
   mascot + a title-surround animation. The mascot's own motion is *additional*, never a
   replacement for those two.

## Canvas anatomy (1280 × 380)

```
┌───────────────────────────────────────────────────────────┐
│  LEFT  (x: 60–720)            │  RIGHT (x: 760–1200)         │
│   • Title (big, gradient)     │   • ONE BOLD, ANIMATED       │
│   • Subtitle (muted)          │     mascot / core-concept    │
│   • Tag pills (0–2 keywords)  │     object (NO ring frame),  │
│   • Optional frosted panel    │     in open space; soft      │
│                               │     non-ring backdrop glow   │
└───────────────────────────────────────────────────────────┘
  Background: vibrant multi-stop gradient (blend 2–3 hues) = rich, colorful.
  Soft decorative layer: ONE faint non-ring glow / scattered dots (NOT a containing circle).
```

Hard constraints (enforced by the validator):
- Root `viewBox` MUST be exactly `0 0 1280 380`.
- The hero motif is a `<g transform="translate(cx,cy)">` with `cx in [760,1200]`. Keep
  every shape's **local** coordinate within ±260 of that anchor (no absolute coords
  that drift off-canvas).
- NEVER put a `rotate`/`scale` `<animateTransform>` on the SAME `<g>` that carries the
  `translate()` base — SMIL defaults `additive="replace"` and wipes the position,
  flinging the motif off-canvas (you'd see only a stray dot). Nest animation in an inner
  `<g>` instead.

## Authoring process (do this every time)

1. **Read the full README; synthesize a content-driven concept** (see "Read everything
   first"). Pick ONE signature object that represents the *whole* project — not a pun on
   the name. A blog → an open book with a writing nib. ChainPass → a self-sovereign
   *verifiable-credential* card flowing through a decentralized identity network into
   cross-border payment. Invent the object; don't reach for a library.
2. **Sketch ONE bold mascot / core-concept object as raw SVG shapes** (`path`/`circle`/
   `rect`/`polygon`), centered on a translate anchor in the right zone (cx in [760,1200]).
   Draw it once, by hand, with `stroke-width` 6–12. Then make it ALIVE: nest its motion
   (bob / float / rotate / swing / pulse) in an *inner* `<g>` with `<animateTransform>`.
   Add ONE soft, **non-ring** backdrop glow (blob / dots / gradient halo) for depth — nothing more.
3. **Give the mascot a life motion that fits its meaning** — a bouncing tomato, a spinning
   coin, a flying frisbee, a sprouting seedling, a blinking cursor. Purposeful, characterful,
   not decorative noise. Pure SMIL (`<animate>` / `<animateTransform>` / `<animateMotion>`),
   because GitHub strips `<style>`/`<script>`. Never put the motion on the SAME `<g>` as the
   base `translate()` — nest it.
4. **Add the two mandatory motion layers** (see "Two mandatory motion layers"):
   a banner-wide sweep AND a title-surround animation. These are required, not optional.
   (The mascot's own motion is on top of these two.)
5. **Choose a RICH, multi-color palette from scratch**: a vibrant **multi-stop gradient**
   (blend 2–3 hues) for the background PLUS **2–3 accent colors** on the mascot. Colorful and
   diverse — not a single deep base + one accent. It must not coincide with a sibling repo's
   hue family — check the existing `banners/` folder first. Distinct, lively hue is mandatory.
6. **Compose the left column**: gradient title, muted subtitle, 0–3 tag pills. Optional
   frosted panel behind the text if contrast needs help.
7. **Validate** (`validate_banner.py`) — Rule 1–4 technical + Rule 6 uniqueness vs the
   `banners/` baseline + **Rule 7 motion layers**. Fix until all PASS.
8. **Push** (see `verification.md`).

## DO / DON'T

**DO**
- Make the mascot's *silhouette* unique to the repo.
- **Use BOLD strokes** (`stroke-width` 6–12) on the mascot.
- **Use RICH multi-color palettes (≥ 3 colors)**: vibrant multi-stop gradient + 2–3 accents.
- Make the hero an **ANIMATED mascot** (bob / float / rotate / swing) nested in an inner
  `<g>` — it should feel alive, like a character or key concept in motion.
- Compose with **one focal mascot + generous negative space** — let it breathe (大气).
- **NO circular badge frame** around the mascot — let it move freely in open space.
- **Always include BOTH mandatory motion layers**: a banner-wide sweep (≥ 600px travel)
  and a title-surround animation. They are required on every banner, not a bonus.
- Vary animation *type* repo to repo (don't give everyone a sweep).
- Pick a fresh, lively hue family per repo.
- Keep motion purposeful and meaningful (mascot life + the 2 layers, not 10).
- Respect `prefers-reduced-motion` intent (gentle loops are fine).

**DON'T**
- Don't copy a shape, path `d`, or motif group from another banner — author yours.
- Don't "reuse a motif and just change the color." That is the exact anti-pattern this
  skill exists to prevent.
- Don't import/generate from a shared motif or preset file.
- Don't **stack many small elements** (coins + satellites + cards + arrows at once) — one
  focal mascot only. "元素堆叠瞎用" is explicitly forbidden.
- Don't use **thin/hairline strokes** for the hero — it kills the bold feel.
- Don't go **monochrome / single-accent** — be colorful (≥ 3 colors).
- Don't box the mascot in a **circle / ring frame**.
- Don't overload the canvas; one hero object + its life motion.
- Don't let text collide with the mascot or run off the 1280 edge.

## Tone & consistency (the "family" feel)

Banners should feel related through *craft*, not through *shared parts*:
- Same canvas size, same title typography rhythm, same tag-pill treatment.
- Same soft decorative background language (blurred orbs / faint grid / blobs).
- Otherwise: each repo's object, palette, and motion are its own.

## Accessibility

- Title text must meet contrast vs its background (aim ≥ 4.5:1; large text ≥ 3:1).
- If the background is busy, put a frosted/translucent panel behind the text.
- SVG root carries `role="img"` + `aria-label="<repo name>"`.
- Animations are decorative; the static first frame must still read correctly.
