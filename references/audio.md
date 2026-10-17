# Audio: TTS, recorded voice, music, SFX, loudness

Numbers are starting points, not standards. Always listen (or ask the owner to listen) on a phone speaker.

## TTS (ElevenLabs)

- Use the **newest flagship model** — run `list_models`, pick the highest `eleven_vN` (not Turbo/Flash for production). When copying `tts.py` from an older project, update `model_id`. Re-measure speed and tag behaviour on a new model version and log it. Don't regenerate already-approved audio on a model upgrade unless asked.
- **Library voices only.** Never `text_to_voice` / `create_voice_from_preview` for a character. If nothing fits, ask which existing voice to use.
- Narrator consistency vs variety: one recognisable narrator (ideally the owner's own cloned voice — parasocial trust); side characters rotate through library voices and never repeat in consecutive reels. Log which voice each video used.
- Before a full run, make a 3-turn sample per voice and get approval. Starting point: stability ~0.4–0.5 (fully "Creative" hallucinates in non-English), similarity 0.75.
- Tone target: warm, curious, sometimes playful and energetic — "serious" means precise, not sad. Energy also comes from text: short sentences, `!`/`?`, interruptions with `—`, short reactions.
- v3+ audio tags: about one every 2–3 turns (`[excited]`, `[curious]`, `[laughs]`, `[sarcastic]`, `[mischievously]`, `[whispers]`, `[sighs]`, `[exhales]`, plus proven `[thoughtful]`, `[warm]`). `[quiet]`/`[sighs]`/`[thoughtful]` only for deliberate moments — used repeatedly they make the voice sound tired. Never a tag against the voice's nature.
- STT (`scribe_v1`) verifies wording and gives word times, but cannot catch vowel-level mispronunciation.
- The ElevenLabs MCP `speech_to_text` may only read files from a sandboxed folder; for project files call the REST endpoint with curl (`scripts/stt_check.py`).

### Persian (and other Arabic-script) diacritics

- Add harakat to the TTS `text` field only; captions stay plain.
- Always mark kasra-ye ezafe (`دفترچهٔ گاردِ جاویدان`, `صفحهٔ هفتِ…`) and every short or ambiguous word (`تَنهاشون نَذار`, `رَصَد`, `سَنَد`, `کِیف` vs keyf).
- Glue the colloquial object marker «رو» to the word (`گوشیتو`, `روزِ بعدو`) — a separate «رو» is read «رُو».
- A misplaced diacritic is worse than none (`دیِ` was read "di"; write `دِی‌ماهِ`). Re-read once before TTS.
- Diacritize a risky word **every** time it appears — the model can get it right in one turn and wrong in another.
- Don't offer retroactive re-voicing of finished videos for diacritics.

## Recorded human speech (interviews, collabs, webcam)

Chain chosen in a blind A/B (ElevenLabs Isolator vs VEED vs VEED+Lava-SR → VEED+Lava-SR won):
1. Full uncut WAV per speaker → fal `veed/clean-audio` (`output_format: wav`, defaults) → `fal-ai/lava-sr` (`audio_format: wav`, `denoise: false`). ≈ $0.08 for a two-person reel.
2. Check alignment with the original (expect 0 ms). Keep STT word times from the original.
3. Light polish: HPF, small 250–300 Hz cut, gentle compression, de-ess, −16 LUFS per speaker. No extra presence/air EQ (VEED already adds it).

Generic voice chain reference (when not using the above): denoise/isolate → HPF 80–120 Hz → cut 200–400 Hz mud → compressor 3:1–6:1, 3–6 dB GR, attack ~5 ms, release ~80 ms → presence +2–3 dB at 3–5 kHz, gentle air 10–15 kHz → de-esser after the compressor (4–10 kHz) → each speaker to −16 LUFS.

Other fal audio tools: `fal-ai/deepfilternet3` ($0.001/s denoise), `fal-ai/elevenlabs/audio-isolation` ($0.10/min), `fal-ai/demucs` / `sam-audio/separate` (music separation — not needed for clean speech).

## Music

- Clearly audible but under the voice: **~10–13 dB below dialogue under speech**, raised in pauses, cover and end card. Measure the bed's LUFS first and set the gain from that (e.g. gain ~0.17 on a −12.9 LUFS bed with voice at −16; ~0.32–0.36 in pauses).
- Duck from a speech-activity curve (e.g. 10 Hz envelope → `duck.json`) rather than a fixed low level. Ducking 6–12 dB, attack 30–80 ms, release 250–700 ms (shorter pumps).
- For explainers, a narrator + music bed beats a trending song.
- Loop shorts: the music/ambience of the last second matches the first; no fade-out, no ending hit, cut the final breath.

## SFX

- Short, matched to the visual style, ~6–10 dB under speech, never on the speaker's key word.
- Refresh SFX per series (generate new ones with ElevenLabs sound generation) instead of reusing the same five whooshes/stamps.

## Loudness and mastering

- Instagram publishes no official spec (sources range −16 to −10 LUFS). Target **−14 LUFS integrated, true peak −1 to −1.5 dBTP**.
- Two-pass `loudnorm` (`measured_*` + `linear=true`) — single-pass landed at −15.1 instead of −14.0. `scripts/master.sh`.
- TV / broadcast deliveries: EBU R128 −23 LUFS.
- After mastering: ebur128 check, re-transcribe the final audio to make sure no words dropped, listen on a phone.

## Voice → character matching

Before designing any lip-sync face for existing audio: median F0 (male ~85–155 Hz, female ~165–255 Hz) + transcript cues. State the result in the plan.

```bash
python3 -c "import sys,numpy as np,librosa; y,sr=librosa.load(sys.argv[1],sr=16000,duration=60); f,_,_=librosa.pyin(y,fmin=60,fmax=400,sr=sr); print(round(float(np.nanmedian(f))),'Hz')" voice.wav
```
