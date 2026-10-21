# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DatasetCreator turns annotation files collected with the [AffecTube](https://github.com/AffecTube/AffecTube) browser extension into an emotion-labeled video dataset: it merges per-annotator annotations, optionally downloads the YouTube videos, and cuts labeled fragments with ffmpeg.

## Commands

```bash
pip install -r requirements.txt   # Python 3.10+ required by yt-dlp; yt-dlp, ffmpeg-python (also needs the ffmpeg binary on PATH)
python dataset_creator.py -h      # list options
python dataset_creator.py -f videos_annotations.json -i ../annotations -o dataset -d
python dataset_creator.py -m      # only write merged annotations JSON, no video processing
python dataset_creator.py -r      # only write raw (unmerged) annotations JSON
```

There are no tests, linter, or build step.

## Architecture

- `dataset_creator.py` is a top-level script (no `main()`): it loads `config.json` from the **current working directory** into a module-global `config` dict, then `parse_options()` overrides keys from CLI flags. All functions read settings from that global. Run it from the repo root.
- `video_downloader.py` — `video_download(code, out_dir)` downloads the best mp4 video + m4a audio via yt-dlp (merged by ffmpeg) to `<out_dir>/<code>.mp4`, skipping if it already exists.

Pipeline:
1. `process_annotation_files()` reads every JSON file in `input_dir`. Each file is one annotator × one video: top-level `videoURL` (YouTube video code) and `nickname`, plus any dict-valued entries treated as events with `startTime`, `endTime`, `label`. Events are grouped by video code and sorted by `startTime`.
2. `merge_annotations()` merges overlapping events per video. Events longer than `max_fragment_size` seconds are dropped. A merged fragment is kept only if `distinct annotators in fragment / distinct annotators of the video >= acceptance_threshold`. With `match_labels: true` overlaps are merged per label (`merge_annotations_match_labels`); otherwise any overlapping events merge into one fragment with a set of labels (`merge_annotations_any_label`).
3. For each video, optionally download, then `generate_annotated_fragments()` trims `<code>_<start>-<end>.mp4` (times in seconds, 2 decimals, margin included) into `output_dir` with `margin` seconds added on each side (start clamped at 0), and writes the adjusted `startTime`/`endTime` and `filename` back into the annotations.
4. The final list is written to `output_filename` as JSON. Without `-d`, source videos must already be in `output_dir` as `<code>.mp4`, otherwise the script exits with an error.

Untracked local data directories (`dataset2/`, `dataset3/`, `experts/`) hold generated datasets and source videos; they are not part of the code.
