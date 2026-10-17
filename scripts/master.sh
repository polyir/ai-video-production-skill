#!/bin/zsh
# Two-pass loudness master (video stream copied), then QC: loudness, black frames, freezes, duration.
# usage: master.sh <raw.mp4> <out.mp4> [target_LUFS=-14] [true_peak=-1.5]
# Broadcast/TV delivery: master.sh raw.mp4 tv.mp4 -23 -1
# zsh note: write ${var}:… inside strings — "$off:linear" would be read as the :l modifier.
set -e
RAW=$1; OUT=$2; I=${3:--14}; TP=${4:--1.5}
[[ -f $RAW && -n $OUT ]] || { echo "usage: $0 raw.mp4 out.mp4 [LUFS] [TP]"; exit 1; }
J=$(ffmpeg -hide_banner -i "$RAW" -af loudnorm=I=${I}:TP=${TP}:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
read ii itp ilra ith off <<< "$(echo $J | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['input_i'], d['input_tp'], d['input_lra'], d['input_thresh'], d['target_offset'])")"
ffmpeg -v error -y -i "$RAW" -c:v copy -af "loudnorm=I=${I}:TP=${TP}:LRA=11:measured_I=${ii}:measured_TP=${itp}:measured_LRA=${ilra}:measured_thresh=${ith}:offset=${off}:linear=true,aresample=48000" -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "== loudness"; ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tail -2
echo "== blackdetect (verify hits by eye — dark 'points of light' shots give false positives)"
ffmpeg -hide_banner -i "$OUT" -vf blackdetect=d=0.5:pix_th=0.1 -an -f null - 2>&1 | grep black_start || echo none
echo "== freezedetect"; ffmpeg -hide_banner -i "$OUT" -vf freezedetect=n=0.002:d=6 -an -f null - 2>&1 | grep freeze_start || echo none
echo "== format"; ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration,size -of csv=p=0 "$OUT"
