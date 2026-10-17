# Scripted production pipeline

Proven on 12-minute episodes (91 turns) and 80-second reels. Everything downstream is keyed to speech turns, so changing one line of audio re-times the whole edit automatically.

## Folder layout per video

```
<video>/
  script_fa.md / script_en.md     approved script
  storyboard.md                   shots: time, layer (code / AI / lip-sync / 3D), fresh/reused, asset
  SOURCES.md                      footage/music/photo sources + licences
  UPLOAD_METADATA.md              caption, hashtags, collaborators, voices used, post IDs
  turns.py                        T = [(section, speaker, text), ...]; VOICES = {speaker: voice_id}
  tts.py  stt_check.py  build_audio.py
  audio/turns/*.mp3  audio/trimmed/*.wav  audio/narration.wav  audio/timing.json
  fal/jobs.json  fal/out/        (scripts/fal_jobs.py state)
  hedra/jobs.json                lip-sync asset/generation ids
  remotion/                      composition; src/timing.ts is generated
  master.sh                      two-pass master + QC
```

## Steps

1. **`turns.py`** — list of `(section, speaker, text)`. `|` marks a caption break inside a turn. Speaker letters map to library voice IDs. TTS text carries diacritics/audio tags; caption text is derived without them.
2. **`tts.py`** — batch TTS, one file per turn, skips existing files unless IDs are passed. Use the newest flagship model (`list_models`), `language_code` set, key from Keychain/env (never printed). Re-run single turns by ID.
3. **`stt_check.py`** (`scripts/stt_check.py`) — transcribe every turn (ElevenLabs `scribe_v1`), similarity vs script, flag < 0.85. Very short lines score low without being wrong. STT does **not** catch vowel errors — the owner listens to names and ambiguous words.
4. **`build_audio.py`** — trim leading/trailing silence (`silenceremove` both ends via `areverse`), place turns with gaps (same section ~0.3 s, new section ~1.3 s, explicit extra gaps for title cards), mix with `adelay` + `amix normalize=0`, loudnorm −16 LUFS, write `timing.json`, `remotion/src/timing.ts` (`turns`, `captions`, `SPEECH_END`) and an SRT. Captions are split by `|` proportionally to character length.
5. **Visual assets** — reference images (free agents or fal), then I2V via `scripts/fal_jobs.py`, then lip-sync per turn (one Character-3 job per turn from the same key image; the avatar clip is muted, audio comes from narration).
6. **Remotion** — every visual event is anchored to a turn start: `T('t045') + 6.5`, never a hard-coded second.
7. **Render → `master.sh`** — two-pass loudnorm −14 LUFS, TP ≤ −1.5 dBTP, then ebur128, blackdetect, freezedetect.
8. **Review cut** to owner → publish after approval → calendar + analytics log.

## Speed / length facts

- Persian narration: ~120–126 words per minute of final video (ElevenLabs v3/v4). Estimate length before TTS; cut the script, not the audio.
- In `eleven_v4`, `voice_settings.speed` has no measurable effect. Shorten with `atempo` ≤ 1.15 (pitch-preserving) cut at sentence boundaries, or fewer words.
- Hook first sentence ≤ ~3 s. Generate 3 takes of the hook, STT them for word times, keep the shortest correct one; use the word times to sync hook visuals.
- When a hook pulls the next sentence forward, cut the repeated words using STT word times.

## Two-person / recorded-speech videos

- Per-speaker full WAV → VEED Clean Audio → Lava-SR → light polish → −16 LUFS each (see `audio.md`).
- Edit decision list from STT word times (`build_audio.py` EDL) — cut long answers at word boundaries; keep a hard length cap.
- Check alignment of enhanced audio against the original (should be 0 ms offset); keep word timings from the original.
- Match eye lines between speakers (see `short-form.md` framing) and colour-match skin (see `ai-generation.md` LUTs).

## Shorts from a long episode

- Plan shorts and their hooks during scripting, not after.
- Cut the needed part of the master with ffmpeg first and give Remotion the small file — deep `trimBefore` into a 400 MB master kills the render browser.
- Phone screens: the mid video band of a short needs ~1.35× the brightness of the episode grade.

## YouTube publishing lessons

- An uploaded video file cannot be replaced; a fix means a new upload. Upload and verify all replacements (schedule, thumbnail, subtitles) before deleting old ones so the schedule never has a gap.
- A dropped resumable upload may still have created the video — check before retrying.
- Linking a Short to its main video (`Related video`) is Studio-only, not in the Data API.
- Schedule = upload private with `publish_at`, then thumbnail, then subtitles, then log the ID.

## Deliverables per episode

Script, scenario, final storyboard, source list (footage + music + licences), final narration, Remotion project + master, one or more shorts, upload metadata, calendar + analytics rows.
