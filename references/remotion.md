# Remotion — patterns and gotchas

## Three visual layers

| Layer | When | How | Cost |
|---|---|---|---|
| 1. Code animation | any concept, number, comparison, recap, rule, allegory | Remotion + SVG (`interpolate`, `spring`, `strokeDashoffset`) | 0 |
| 2. Illustration + I2V | history/myth, atmosphere | reference image → fal I2V | $ |
| 3. Lip-sync avatar | a character speaking directly (fictional narrator, documented-quote caricature, witness) | Hedra Character-3 from key image + turn audio | $ |

Reusable scene components worth building once per house style: `Still` (Ken Burns), `ClipStill`, `Lip`, `Chip` (source/AI label), `Quote` (quote with source), `Big` (spring word), `Scrim`, `TitleCard`, `Recap`, `RoadMap`, `Gauges`, `Timeline`, `Rules` (rule cards), `EndCard`, and an **allegory scene** pattern: a 2D SVG world with a camera (zoom/pan) driven by time marks from `timing.ts`. Write new components to be reusable in the next video.

## Colour as narrative: cold → warm arc

Problem/obstacle/repression in dark cold navy (`#05080f`–`#13213b`), low light, silhouettes; hope/action/solution in ochre, gold, pomegranate red, warm dawn light. Put the colour turn exactly on the script's turning point. At least one colour "sunrise" per video. Keep one fixed style prompt for all images of a video.

## Timing

- Drive the timeline from generated `timing.ts`, never from the storyboard table, so every cut lands on a speech boundary.
- No empty gaps between beats — extend each beat to the next beat's start, or pauses show black.
- **Lip-sync clips start at the start of their own turn** (`T(id)`). If the cut starts at 0 but the turn at 0.6 s, the mouth leads the voice by 0.6 s.
- A long beat needs a *set* of visuals, not one clip; `<Video>` holds its last frame after the end.
- Slow clips with `playbackRate` (down to ~0.5 for calm abstract shots) to fill a gap; compute the rate from the **usable** duration if the head is trimmed, or the clip runs past its end and freezes.
- 5/10 s clips: slow to ≤ 2× with a `ClipStill`, then crossfade into a Ken Burns of the same image.
- Any static shot > 8 s gets I2V or at least Ken Burns. Wrap every cut in a `Drift` (≈4% zoom + 0.6% pan) so no card is ever frozen.
- Hard cuts between shots, not fades — a fade between two dark shots dips to pure black. Fades only on first/last shot.
- Shots that deliberately end in darkness/stillness: trim a short tail so the cut doesn't land on a dead frame.
- AI clips with audio tracks: `muted`.
- Put each AI clip in its own `<Sequence>` so playback starts exactly when shown; animating opacity alone can let the video play invisibly.

## Layout gotchas

- **Never use `<Sequence>` inside a flex/column flow to swap cards** — a Sequence renders an absolutely-positioned AbsoluteFill, so cards stack. Swap with a frame condition.
- `public/` rejects symlinks pointing outside it (404 on render; the bundler copies the link verbatim). Use **hard links** (`ln`, same APFS volume) or copies for files; folder symlinks may work. Re-link new files before rendering.

## Text (incl. RTL / Persian)

- One font family per brand; load all weights via `src/fonts.ts` from `public/fonts/`. Weight map: titles 900, subtitles/stamps 800, captions 700–800, small labels 600–700.
- Vazirmatn is ~10% wider/taller than SF Arabic — scale sizes ×0.9 when porting; cover titles `whiteSpace: 'nowrap'`; check line breaks with `remotion still`.
- Legibility: **stroke, not boxes** — `WebkitTextStroke: '<w>px #050403'` + `paintOrder: 'stroke fill'` + soft `textShadow`. Widths: cover titles/big numbers 14–16 px, moving cards 13, captions 11, small labels 6–9. Boxes only for intentional cards (chips, stamps, quotes, share card).
- Line height with Vazirmatn: titles 1.45, captions 1.6 (1.22 made lines collide).
- Check cover + at least one frame over the **brightest** shot before rendering.
- RTL layouts: dark scrims go on the right, behind the title.

## 3D

Default: at most one 3D hero scene per reel, and only when the topic has spatial shape (layers/hierarchy, map/geography, scale/volume, physical object). Lists, text and simple numbers stay 2D. 3D is a tool, not a design family — a fully-3D reel is fine when the owner asks for it, but don't make it the new repeated template.

**Stack that works together (Oct 2026):** Remotion 4.0.536, `@remotion/three` 4.0.536, `three@0.186.1`, `@react-three/fiber@9.8.2`, `@react-three/drei@10.7.9`, `@react-three/postprocessing@3.2.0`, `postprocessing@6.39.5` (older pins fail npm peer resolution). Keep `@remotion/*` at exactly the project's Remotion version.

**Reusable kit:** `assets/remotion-3d/kit3d.tsx` — `Stage`, `Cam`, `Glb`, `Card`, `Label3D`, `useCanvasTex`, `Post` (bloom/tone mapping/vignette with the warmup fix below) — and `assets/remotion-3d/stills.mjs` (one bundle, many `renderStill` calls: 15 frames in ~12 s instead of one CLI call per frame).

Rules:
- Animate only with `useCurrentFrame()`, `interpolate`, `spring` — not R3F's `useFrame`. Camera via a component that sets `useThree().camera` every frame. `<Sequence>` inside `ThreeCanvas` needs `layout="none"`.
- **Always render with `--gl=angle`** — also for audio-only renders (`--codec=wav` still draws frames and hung without it).
- Keep the cold→warm arc in materials and lights.

Render traps (each cost a debug cycle):
- **EffectComposer frames come out blank** unless the canvas has `gl={{preserveDrawingBuffer: true}}` **and** a per-frame warmup component (`delayRender` → two `advance()` calls in rAF → `continueRender`). ThreeCanvas's own single advance runs before the composer is wired up.
- **GLB (`useGLTF`) loads after the frame advance**, so the model is missing from the capture. In the GLB component, re-advance twice under `delayRender` after load.
- **drei `<Html>` is unreliable in renders** (missing or misplaced). Use canvas-texture billboards (`Label3D`) or plain HTML overlays at fixed screen positions. Text and logos never as 3D text.
- Canvas-2D text on a `CanvasTexture` shapes Persian/RTL correctly (font loaded via `@remotion/fonts`); set `toneMapped={false}` on text materials.
- ACES tone mapping crushed bright screens → use AgX.
- `transmission` glass renders black under the composer → transparent physical material + gold `edgesGeometry` edges.
- Timing: a full 82 s 1080×1920 3D render ≈ 130 s at concurrency 4 on Apple Silicon.

Real 3D objects instead of AI video: generate an isolated-object image (plain grey background, 3/4 view, no text) → image-to-3D GLB (see `ai-generation.md`, Trellis 2) → orbit it with a code camera. No last-second I2V breakage, full camera control.

## Grading mixed sources

- Stock daytime footage is much brighter than AI shots: separate grades (AI shots: tint only; real footage: brightness ~0.6, saturation ~0.55).
- Some AI shots average YAVG ~25/255 — measure each clip and lift dark ones; heavy bottom gradient only on shots with titles.
- "Film grain overlay" stock is a bright noise plate — overlay only, never a full-frame shot.

## QC before and after render

- Before any full render: `remotion still` on ≥ 4 key frames (first, last, suspicious points). A 35-minute render is an expensive way to find a logic bug.
- After render: `freezedetect=n=0.002:d=6`, `blackdetect` (false positives on "points of light on black" — verify with real-frame YAVG), ebur128, duration, 1080×1920 / 30 fps, audio track present, caption legibility.
- **Always look at a frame grid (~18 points across the master)** — readable-text artefacts and off-palette shots are caught only by looking. For AI motion, a 1-fps contact sheet over the clip range, not a few stills.
- Check thumbnails at ~320 px wide.
- Verify frame 0 of the video equals `cover.png`.
- `scripts/qc.sh` automates the grid, contact sheet and detectors.
