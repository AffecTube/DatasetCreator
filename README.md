# DatasetCreator
_DatasetCreator_ script processes annotation data collected with the [AffecTube](https://github.com/AffecTube/AffecTube) extension,
downloads videos from YouTube and generates emotion-labeled video fragments.

## Requirements

- Python 3.10 or newer (required by [yt-dlp](https://github.com/yt-dlp/yt-dlp))
- [FFmpeg](https://ffmpeg.org/) available on `PATH` (used for merging downloaded video/audio streams and for cutting fragments)

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## Usage

Run the script with `-h` option to view all available options. Alternatively, set
the required setting in the `config.json` file. 

```bash
$ python dataset_creator.py -f videos_annotations.json -i ../anotations -o dataset -d

Downloading https://youtu.be/Cu7pKk8KpOY ...
Video downloaded: ./dataset/Cu7pKk8KpOY.mp4
Processing Cu7pKk8KpOY.mp4, extracting 5 fragments
Extracting: ./dataset/Cu7pKk8KpOY_5.21-16.14.mp4
Extracting: ./dataset/Cu7pKk8KpOY_31.50-42.08.mp4
Extracting: ./dataset/Cu7pKk8KpOY_58.12-71.40.mp4
Extracting: ./dataset/Cu7pKk8KpOY_94.03-103.77.mp4
Extracting: ./dataset/Cu7pKk8KpOY_120.66-134.20.mp4
Downloading https://youtu.be/8ZUQGOUOO_M ...
Video downloaded: ./dataset/8ZUQGOUOO_M.mp4
Processing 8ZUQGOUOO_M.mp4, extracting 4 fragments
Extracting: ./dataset/8ZUQGOUOO_M_0.00-12.35.mp4
Extracting: ./dataset/8ZUQGOUOO_M_27.80-39.12.mp4
Extracting: ./dataset/8ZUQGOUOO_M_45.03-58.90.mp4
Extracting: ./dataset/8ZUQGOUOO_M_76.44-88.10.mp4
...
```

Fragment files are named `<youtube_id>_<start>-<end>.mp4`, where start and end are times in seconds
(with the margin applied), matching `startTime`/`endTime` in the output JSON.
