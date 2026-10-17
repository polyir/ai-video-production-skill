---
name: ai-video-production
description: End-to-end know-how for producing short-form and long-form social videos (Instagram Reels, YouTube, Shorts, explainers, talking-head and two-person collabs) with AI tools — ElevenLabs TTS/music/SFX, fal.ai image-to-video, Hedra Character-3 lip-sync, code-built Remotion motion design, ffmpeg mastering and QC — plus hook/CTA writing, Instagram growth rules and post-performance analysis. Use whenever a project involves scripting, storyboarding, generating, editing, rendering, mastering, publishing or analysing a video or reel, choosing AI video/image/voice models, budgeting AI generation spend, cleaning recorded voices, colour-matching speakers, or judging why a post did well or badly. Distilled from the Iran 2.0 Series 2 production (Sept–Oct 2026).
---

# AI Video Production

A production system that has shipped 40+ reels and long episodes. It is opinionated: every rule below came from a real failure or an explicit owner decision. Project-specific choices (brand, logos, voices, budgets) are **not** here — each new project sets its own (see "Per-project setup").

## Core principles

1. **Approval gate before spending.** Script + storyboard go to the owner first; no paid generation (TTS, images, video, lip-sync) until both are approved. Footage research and source lists are fine before approval. Any substantial content change after approval is shown again. Every public upload needs its own approval.
2. **The owner decides dates.** Never propose production or publish dates/schedules unless the owner set a standing cadence. Keep a content calendar file and update it right after every production and every publish (status, real date, post ID) — the task isn't done until it is.
3. **Motion design first, AI second.** Before ordering any AI clip ask: "can this be built in code?" If something can be *shown* (map, gauge, timeline, checklist, number, comparison, rule card, allegory) build it in Remotion/SVG at zero cost. AI only for what must be *seen* (faces, historical scenes, paintings, atmosphere). Every video — including 30-second reels — uses code-built motion design. Label each storyboard shot's layer (code / AI / lip-sync) and state the motion-design share.
4. **Every AI video starts from an approved reference image** (image-to-video, reference-to-video or first-last-frame). No text-to-video.
5. **Audio always from a dedicated audio tool** (ElevenLabs): narration, hooks, music, SFX. Force video models' own audio off (it also often doubles price).
6. **Budget caps are enforced by tooling, not memory.** Use `scripts/fal_jobs.py` with a cap; it refuses to submit if the estimate exceeds the cap or any image costs ≥ $1.
7. **I cannot hear audio or reliably judge faces.** Measure instead: F0 for voice gender, LUFS for loudness, STT for wording, stills/contact sheets for visuals. Ask the owner to listen to names and ambiguous words.
8. **Log decisions.** Keep a `DECISIONS.md` (owner rules + lessons, dated) and a `PRODUCTION_WORKFLOW.md` (current rules). Knowledge/research goes in a separate file with confidence levels; it becomes a rule only when the owner approves.

## Production order

1. Review source text and goal → 2. draft script + storyboard (mark shorts and their hooks now; cap reused footage at ~25%) → 3. extract exact asset list → 4. check existing assets, download only gaps from licensed sources → 5. verify downloads (topic, length, resolution) → 6. finalize script/storyboard against real files → 7. **show owner, stop until approved** → 8. generate (TTS → reference images → I2V → lip-sync) → 9. assemble in Remotion + technical QC → 10. review cut for publish approval → 11. upload after approval → 12. update calendar + analytics log.

Scripted pipeline (details in `references/pipeline.md`): `turns.py` → `tts.py` → `stt_check.py` → `build_audio.py` (→ `timing.ts` + captions) → Remotion → `scripts/master.sh` (two-pass −14 LUFS + QC).

## Default tool split (override per project)

| Job | Tool | Notes |
|---|---|---|
| Images | Free agents first (Codex image_gen / Antigravity via a cross-agent MCP) if available; else fal (`nano-banana-2` new, `nano-banana-pro`/`edit` for style consistency and i2i; Flux 2 Pro as fallback when Nano Banana refuses) | target ≤ $0.30/image, never ≥ $1 |
| Video (I2V) | fal: Veo 3.1 (incl. lite/fast, first-last-frame for transitions), Gemini Omni Flash 1.1, Wan 3.0, Kling 2.6 Pro | always set resolution explicitly — price depends on it |
| Lip-sync | Hedra `hedra-character-3` only | often cheaper per second than I2V → tell the story through a character where possible |
| Voice, music, SFX | ElevenLabs, newest flagship TTS model (`list_models`; never copy an old `model_id`) | library voices only, never designed voices |
| Recorded-voice cleanup | fal `veed/clean-audio` → `fal-ai/lava-sr` (denoise off) → light polish | enhancement, not generation |
| Edit / render | Remotion (+ `@remotion/three` for at most one 3D hero scene) | |
| Master / QC | ffmpeg | `scripts/master.sh`, `scripts/qc.sh` |

Model/price details and traps: `references/ai-generation.md`.

## Hard-won rules (the ones that cost money)

- **Never design a new TTS voice** (`text_to_voice`). Designed voices mispronounce non-English and STT can't catch vowel errors. Cast from the existing library; if nothing fits, ask.
- **Match character to voice before generating a lip-sync face.** Measure median F0 (~85–155 Hz male, ~165–255 Hz female) and read the transcript. A male avatar on a female voice wasted a whole render.
- **Never assume the gender or identity of a person on camera** in the owner's footage — it is usually the owner.
- **Persian/Arabic-script TTS needs diacritics** (esp. ezafe kasra and short ambiguous words) in the TTS text only; captions stay plain. A misplaced diacritic is worse than none. See `references/audio.md`.
- **Music must be clearly audible**: ~10–13 dB under speech with ducking, louder in pauses/cover/end card. Fixed beds at gain 0.06 were inaudible.
- **`fal_pricing` returns only the lowest tier** (e.g. 360p). Budget from the per-resolution table.
- **Real people's photoreal faces are not reconstructed.** Use silhouettes/back views/hands, labelled "symbolic reconstruction". Obvious cartoon caricatures of public figures may speak only documented, dated, sourced quotes, labelled as such.
- **Never put readable text in an image/video model prompt** — it produces gibberish; add text in Remotion. Don't put character names in prompts (the model writes them on the image); say "plain, no symbols" for flags/props.
- **Watch the end of every AI clip** — content often breaks in the last seconds; shorten `clipLen`.

## Short-form rules (summary — full version in `references/short-form.md`)

- Hook works on 3 layers at once in 0–3 s: frame 0 visual, first spoken line (starts at 0.05 s, no preamble, main promise by second 4), on-screen text readable without sound. ≤ 8 words. Write 2–3 hooks of *different types* per reel.
- Frame 0 = the cover (entry fade reduced to one frame).
- Reel hard cap 160 s, sweet spot ~80–90 s; Instagram only recommends ≤ 3 min to non-followers.
- End: voice = follow with a **reason** (best: a named teaser of the next part); on-screen = content question; caption = comment question + follow. Share invite ("send it to someone who…") only on practical posts.
- Never ask questions that reveal the viewer's group, identity, location or activities when the audience may be at risk.
- ≤ 5 hashtags; main keyword explicitly in caption line 1–2 (captions are search-indexed).
- Rotate visual families, hook types, narrators and cover templates — consecutive look-alike reels get skipped as "the previous post".

## Analysis rules (summary — full version in `references/analytics.md`)

- Compare posts only at equal age (24 h / 48 h / 7 d) and within the same collab status; posts < 24 h are "provisional".
- Outliers (driven by an external big-account share, news event, etc.) are excluded from baselines until their pattern is reproduced by changing parameters you control. **Ask the owner about external shares before crediting the content** — the API can't see them.
- Don't claim shadowban/restriction without evidence from the app's Account Status.
- Collab acceptance timing is unpredictable; don't attribute reach jumps to collabs without evidence.
- Judge success by engagement (shares, saves, comments per reach, follows per 1k reach), not reach alone.
- Two speeds: log data every time; propose rule changes only in a weekly review and only if ≥ 3 equal-age posts show the pattern.

## Per-project setup (ask or read at the start of a new project)

Brand palette, fonts and logo set · narrator voice + rotating side voices · AI-disclosure wording · budget caps per reel/video · allowed/forbidden models · where API keys live (Keychain service names / env vars) · publishing accounts and collaborator map · content calendar and analytics file locations · audience safety constraints · whether the owner can appear on camera.

## Reference files

| File | Read when |
|---|---|
| `references/pipeline.md` | building the scripted TTS → timing → Remotion pipeline; folder layout; deliverables |
| `references/remotion.md` | writing or debugging Remotion compositions, fonts, RTL text, 3D, render QC |
| `references/audio.md` | TTS settings, diacritics, voice chain, music ducking, loudness, SFX |
| `references/ai-generation.md` | choosing/pricing fal models, I2V rules, Hedra Character-3, Omni video edit, matting, LUTs, free image agents |
| `references/short-form.md` | hooks catalogue, CTAs, loop shorts, Instagram ranking signals, curiosity gap, explainer principles, framing |
| `references/analytics.md` | running an Instagram/YouTube analysis, CSV schemas, comparison rules |
| `scripts/fal_jobs.py` | budget-capped fal image/video job runner (estimate / submit / poll / download) |
| `scripts/stt_check.py` | verify TTS turns against the script with ElevenLabs STT |
| `scripts/master.sh` | two-pass loudness master + loudness/black/freeze QC |
| `scripts/qc.sh` | frame grid + contact sheet + technical checks before delivery |
