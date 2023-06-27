# DatasetCreator
_DatasetCreator_ script processes annotation data collected with the [AffecTube](https://github.com/AffecTube/AffecTube) extension,
downloads videos from YouTube and generates emotion-labeled video fragments.

Run the script with `-h` option to view all available options. Alternately, set
the required setting in the `config.json` file. 

```bash
$ python dataset_creator.py -f videos_annotations.json -i ../anotations -o dataset -d

Downloading https://youtu.be/Cu7pKk8KpOY ...
Video downloaded: ./dataset/Cu7pKk8KpOY.mp4
Processing Cu7pKk8KpOY.mp4, extracting 5 fragments
Extracting: ./dataset/Cu7pKk8KpOY_1.mp4
Extracting: ./dataset/Cu7pKk8KpOY_2.mp4
Extracting: ./dataset/Cu7pKk8KpOY_3.mp4
Extracting: ./dataset/Cu7pKk8KpOY_4.mp4
Extracting: ./dataset/Cu7pKk8KpOY_5.mp4
Downloading https://youtu.be/8ZUQGOUOO_M ...
Video downloaded: ./dataset/8ZUQGOUOO_M.mp4
Processing 8ZUQGOUOO_M.mp4, extracting 4 fragments
Extracting: ./dataset/8ZUQGOUOO_M_1.mp4
Extracting: ./dataset/8ZUQGOUOO_M_2.mp4
Extracting: ./dataset/8ZUQGOUOO_M_3.mp4
Extracting: ./dataset/8ZUQGOUOO_M_4.mp4
...
```

