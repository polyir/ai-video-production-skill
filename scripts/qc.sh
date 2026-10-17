#!/bin/zsh
# Visual QC before delivery: an evenly spaced frame grid of the whole video, an optional 1-fps contact sheet
# of a range (to prove AI clips actually move), frame 0 vs cover check, and audio-track presence.
# usage: qc.sh <video.mp4> [cover.png] [range_start_s range_end_s]
# Outputs go to qc/ next to the video. Look at grid.jpg yourself — detectors miss readable-text artefacts
# and off-palette shots.
set -e
V=$1; COVER=$2; RS=$3; RE=$4
[[ -f $V ]] || { echo "usage: $0 video.mp4 [cover.png] [start end]"; exit 1; }
D="${V:h}/qc"; mkdir -p "$D"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
n=18
for k in $(seq 0 $((n-1))); do
  t=$(python3 -c "print(round($dur*($k+0.5)/$n,2))")
  ffmpeg -v error -y -ss $t -i "$V" -frames:v 1 -vf scale=270:-2 "$D/g_$(printf %02d $k).jpg"
done
ffmpeg -v error -y -pattern_type glob -i "$D/g_*.jpg" -vf tile=6x3 "$D/grid.jpg" && rm "$D"/g_*.jpg
echo "grid: $D/grid.jpg"
if [[ -n $RS && -n $RE ]]; then
  ffmpeg -v error -y -ss $RS -to $RE -i "$V" -vf "fps=1,scale=270:-2,tile=6x$(( (${RE%.*}-${RS%.*}+5)/6 ))" -frames:v 1 "$D/contact.jpg"
  echo "contact sheet: $D/contact.jpg"
fi
ffmpeg -v error -y -i "$V" -frames:v 1 "$D/frame0.png"
if [[ -n $COVER && -f $COVER ]]; then
  ffmpeg -hide_banner -i "$D/frame0.png" -i "$COVER" -lavfi "[0][1]scale2ref[a][b];[a][b]ssim" -f null - 2>&1 | grep -o "All:[0-9.]*" | sed 's/^/frame0 vs cover SSIM /;s/$/  (≥0.95 = same; lower = frame 0 differs from cover — fine only if decoupled on purpose)/'
fi
ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 "$V" | grep -q . && echo "audio: present" || echo "audio: MISSING"
ffmpeg -hide_banner -i "$V" -frames:v 1 -vf scale=320:-2 "$D/thumb320.jpg" -y -v error && echo "small-size check: $D/thumb320.jpg"
