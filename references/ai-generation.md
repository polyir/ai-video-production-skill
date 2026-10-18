# AI generation: images, video, lip-sync, edits, matting, colour

Prices are from fal/Hedra pages in Sept–Oct 2026 — re-check before budgeting (`fal_pricing`, model pages).

## Pricing traps

- `fal_pricing` returns only the **lowest tier**. Omni Flash 1.1 shows $0.03/s — that is 360p; 720p is $0.10, 1080p $0.15, 4K $0.30.
- Ambiguous units ("1 unit", "$1 units" for GPT Image, $0.14 shown for Kling) — read the model page and set an explicit `usd` in the job, or skip the model.
- Kling `generate_audio` defaults to on and doubles the price. Veo/Wan/Seedance audio also force off (audio comes from ElevenLabs).
- Always set `resolution` explicitly; defaults are often 1080p.

| Model (fal) | Price | Notes |
|---|---|---|
| `fal-ai/nano-banana-2` | $0.08/img (0.5K ×0.75, 2K ×1.5, 4K ×2) | default for new images |
| `fal-ai/nano-banana-pro` (+`/edit`) | $0.15 | style consistency, i2i (e.g. 9:16 from 16:9) |
| `fal-ai/flux-2-pro` (+`/edit`) | — | fallback when Nano Banana refuses/fails |
| `fal-ai/veo3.1/*` image-to-video, reference-to-video, first-last-frame, extend | full ~$0.20/s 720p–1080p (audio off), 4K $0.40; **Lite 720p ~$0.05/s** (4/6/8 s only) | first-last-frame = shot-to-shot transitions; Lite is the cheapest 720p |
| `google/gemini-omni-flash/v1.1/*` | 360p/720p/1080p/4K = 0.03/0.10/0.15/0.30 $/s | also `end_image_url`; has an `/edit` (v2v) mode |
| `alibaba/wan-3.0/*` | 480p/720p/1080p = 0.05/0.10/0.20 $/s (Prime 0.068/0.14/0.28) | default 1080p |
| `fal-ai/kling-video/v2.6/pro/*` | $0.07/s 1080p audio-off | 5 or 10 s only |
| Seedance 2.x | ~30% cheaper on Hedra than fal | |

Budget example that worked: fal ≤ ~$3.45 per reel and ≤ ~$5.75 per long video (images + clips + tests), lip-sync uncapped. Enforce with `scripts/fal_jobs.py`.

## Free image generation via other agents (if a cross-agent MCP is available)

- **Codex** (built-in image_gen): best brief-following, finals. `mode: implement`, `in_place: true`, `cwd` = target folder → PNG saved there (~936×1664), ~3 min/image.
- **Antigravity**: quick drafts, ~1 min/image (768×1376 JPG); `ask` mode; files land in `~/.gemini/antigravity/brain/<conversationId>/` — copy manually; the job reports "finished" before the image exists.
- One job per image, all sent in parallel (parallel doesn't slow down; two images in one job takes twice as long).
- Neither agent has native video, music or SFX. fal stays for video, ElevenLabs for audio; fal for images only when both agents are down or a precise i2i edit is needed.
- fal can't fetch images from some hosts — `fal_upload` local files first.

## Image prompts

- Fixed style prompt for all images of a video (e.g. "coffeehouse painting: ochre/pomegranate/gold/navy palette, dark outlines, no text").
- No readable text, no logos (add in Remotion). No character names (written onto the image). "plain, no symbols, no religious symbols" for flags/props.
- Covers: 9:16, clean space at top for logo, dark lower ~40% for title; keep the prompt next to the cover file; title/logos in Remotion.
- No photoreal reconstruction of real people's faces.

## Image-to-video

- One subject, one main motion, one slow camera move per shot; 4–6 s.
- Use AI clips between real footage/photos/slides, never as a long standalone block.
- Generate one output normally; re-generate only for technical failure.
- Check the last seconds of every clip (subjects vanish, content breaks) and shorten `clipLen`.
- Weaker/cheap models: avoid faces, hands and complex physical interaction; use them for simple/abstract shots.

## Image → 3D model (GLB)

- `fal-ai/trellis-2` (resolution 1024, texture 2048, decimation 120–200k) gives a clean textured GLB, Y-up, height ≈ 1. Worked first try on both objects tested (fuel pump, refinery). Fallback: Hunyuan 3D v3.1.
- Input image: one isolated object, plain neutral/grey background, 3/4 view, no text or logos (a free image agent is fine).
- `fal_pricing` shows $0.05 per "unit" with an unclear unit — confirm on the fal dashboard; set an explicit `usd` in the job and a small cap (≈ $1.5 for two models).
- Put GLBs in Remotion `public/` (hard links, not symlinks) and load with the kit's `Glb` (see `remotion.md` render traps).

## Lip-sync (Hedra Character-3)

- Only `hedra-character-3` unless the owner approves another avatar model. v3 API: 540p 2.5¢/s, 720p 5¢/s, 1080p 6.25¢/s (separate API wallet from Studio credits; `INSUFFICIENT_BALANCE` = owner must top up). `/estimate` doesn't work for audio-driven models (cost = audio length).
- v3 flow: `upload_file` (image + audio) → `run_model` `{"input":{prompt, aspect_ratio, resolution, duration_ms, start_image:{source:"url",url}, audio:{source:"url",url}}}` → `wait_for_job` (4 s clip ≈ 25 s).
- One generation per turn from the same key image; cut between avatar and other visuals; avatar clip muted, audio from narration.
- Character-3 re-frames wider (character smaller). Crop back in Remotion (`scale 1.3`, origin 50% 30%) and put the clip's last frame underneath so a short clip never leaves a gap.
- Same identity across shots: make 3–4 refs of the same person (close-up / full body × cold / warm grade).
- Synthetic narrators are labelled as such.
- If an API key 403s: a running MCP process may hold a stale key (restart); if still 403 after restart, the key rotated — test with `GET https://api.hedra.com/web-app/public/models`.

## Video edit of real footage (Gemini Omni Flash 1.1 `/edit`)

Used to fix eye contact/framing on webcam talking heads.
- Inputs: `prompt`, `video_url`, `resolution`. Aspect ratio and duration come from the source → pre-build a 9:16 input.
- It won't reframe ("pull the camera back" is ignored): place the subject at the wanted scale on a 720×1280 canvas, smear the shirt down as a placeholder, ask it to render the torso there.
- Same background in every chunk: make one plate, key the subject onto it yourself, prompt "keep the room behind him exactly as it is".
- Prompt order decides what changes. Gaze changed only when eye contact was the **first** instruction and "keep expressions/head motion" was dropped. Gaze still drifts at idle moments.
- Re-voicing is per clip and repeatable: some lines pass the original audio, others come back re-spoken with changed words every time. A prompt forbidding re-voicing is rejected (422, unbilled). Use one chunk per sentence (3–6 s).
- Always STT the output, match words to the original (difflib), retime the video and mux the original audio. For lines that stay re-voiced, fall back to Character-3 lip-sync on a clean Omni frame + original audio.
- 360p drafts test layout/background only; they don't predict 1080p re-voicing.
- Some owners forbid generative edits of real speakers — ask first.

## Green-screen / background removal

- `veed/video-background-removal/fast` with `refine_foreground_edges: true`, `output_codec: h264`. Use only the alpha output (frame-exact with source) + original RGB (VEED's colour is ~1.6 Mbps). $0.008 per 30 frames.
- fal upload limit ~100 MB → re-encode at CRF 20 keeping frames.
- Choke alpha ~1 px and despill the edge band.

## Colour matching real speakers (LUTs)

- Order: correction (white balance, exposure, per-speaker skin match) **then** one shared look. A look on uncorrected footage amplifies problems.
- Skin on the vectorscope skin line (~11 o'clock; ~50–55° hue in Lab), similar chroma and L* across speakers; measure on cheeks, not the whole frame.
- Shared look: gentle S-curve, slightly lifted blacks, soft highlights, +10–20% saturation (skin only +5%), very light split-tone (cool shadows, warm highlights). Plates/B-roll get the look only.
- Build your own 33-point `.cube` LUTs (python → `.cube`, apply with ffmpeg `lut3d`) so licensing and matching are in your hands. Downloaded LUTs: check commercial licence; apply at 30–60% strength.
- Re-measure skin for every new recording.
