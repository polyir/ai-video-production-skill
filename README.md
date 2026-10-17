# ai-video-production — a Claude Code / Codex skill

Practical know-how for producing social videos (Instagram Reels, YouTube, Shorts, explainers, talking-head and two-person collabs) with AI tools: ElevenLabs TTS/music/SFX, fal.ai image-to-video, Hedra Character-3 lip-sync, code-built Remotion motion design, ffmpeg mastering and QC — plus hook/CTA writing, Instagram growth rules and post-performance analysis.

Distilled from the Iran 2.0 Series 2 production (Sept–Oct 2026, 40+ reels and long episodes) by Sina Torabi ([@cnatorabi](https://www.instagram.com/cnatorabi/)).

## Install

**Claude Code** (available in every project):

```bash
git clone https://github.com/polyir/ai-video-production-skill.git ~/.claude/skills/ai-video-production
```

**Codex** (after installing for Claude Code, share the same copy):

```bash
mkdir -p ~/.codex/skills && ln -s ~/.claude/skills/ai-video-production ~/.codex/skills/ai-video-production
```

**Update later:**

```bash
git -C ~/.claude/skills/ai-video-production pull
```

Start a new session afterwards. The skill loads automatically when you work on videos; you can also ask for it by name ("use the ai-video-production skill").

## What's inside

| Path | Content |
|---|---|
| `SKILL.md` | core principles, production order, default tool split, hard-won rules |
| `references/pipeline.md` | scripted TTS → timing → Remotion pipeline, folder layout, YouTube lessons |
| `references/remotion.md` | Remotion patterns, timing, RTL text, 3D, render QC |
| `references/audio.md` | TTS settings, Persian diacritics, recorded-voice chain, music ducking, loudness |
| `references/ai-generation.md` | fal model prices and traps, I2V rules, Hedra, Omni video edit, matting, LUTs |
| `references/short-form.md` | ranking signals, hook catalogue, structure, CTAs, loop shorts, framing |
| `references/analytics.md` | Instagram/YouTube analysis method and comparison rules |
| `scripts/fal_jobs.py` | budget-capped fal.ai job runner (estimate / submit / poll / download) |
| `scripts/stt_check.py` | verify TTS turns against the script with ElevenLabs STT |
| `scripts/master.sh` | two-pass loudness master + QC |
| `scripts/qc.sh` | frame grid, contact sheet, frame-0 vs cover check |

## Requirements for the scripts

`ffmpeg`, `python3`, zsh (macOS default). API keys are read from environment variables or the macOS Keychain — nothing is stored in the repo:

| Script | Env var | Keychain service (fallback) |
|---|---|---|
| `fal_jobs.py` | `FAL_KEY` | `FAL_KEYCHAIN_SERVICE` (default `fal-api-key`) |
| `stt_check.py` | `ELEVENLABS_API_KEY` | `ELEVENLABS_KEYCHAIN_SERVICE` (default `elevenlabs-api-key`) |

Budget caps for `fal_jobs.py`: `FAL_CAP_REEL` (default 3.45 USD), `FAL_CAP_VIDEO` (5.75), `FAL_IMAGE_MAX` (1.0), `FAL_IMAGE_TARGET` (0.30).

Model prices were checked in Sept–Oct 2026 — verify before relying on them.
