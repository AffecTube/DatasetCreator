import json
import os
from optparse import OptionParser

config_filename = "config.json"


def parse_options():
    """
    Parses script options
    """
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="output_filename",
                      help="write JSON output to FILE", metavar="FILE")
    parser.add_option("-i", "--input-dir", dest="input_dir",
                      help="read annotations files from DIR", metavar="DIR")
    parser.add_option("-o", "--output-dir", dest="output_dir",
                      help="write video fragments in DIR", metavar="DIR")
    parser.add_option("-a", "--annotations_only",
                      action="store_true", dest="annotations_only",
                      help="don't produce fragments, only write annotations to file")

    (options, args) = parser.parse_args()

    if options.output_filename is not None:
        config['output_filename'] = options.output_filename
    if options.input_dir is not None:
        config['input_dir'] = options.input_dir
    if options.output_dir is not None:
        config['output_dir'] = options.output_dir
    if options.annotations_only is not None:
        config['annotations_only'] = options.annotations_only


def json_file_to_dict(filename):
    """
    Reads the JSON file
    :param filename: JSON file name
    :return: Deserialized JSON to dict
    """
    with open(filename, 'r') as file:
        return json.load(file)


def json_broken_file_to_dict(filename):
    """
    Reads the "broken" JSON file
    :param filename: JSON file name
    :return: Deserialized JSON to dict
    """
    with open(filename, 'r') as file:
        data = file.read().rstrip().lstrip('"').rstrip('"').replace('\\', '')
    return json.loads(data)


def dict_to_json_file(dict):
    """
    Writes dict to JSON file
    :param dict: dict to be written
    """
    with open(config['output_filename'], 'w') as fp:
        json.dump(dict, fp, indent=4)


def events_dict_to_list(annotations):
    """
    Processes events annotated by single annotator in a single video
    :param annotations: dict with annotations
    :return: list with events, each event is extended with annotator nickname
    """
    events = []
    annotator_nickname = annotations['nickname']
    for key, value in annotations.items():
        if type(value) is dict:
            value['nickname'] = annotator_nickname
            events.append(value)
    return events


def process_annotation_file(filename):
    """
    Processes single annotation file
    :param filename: name of the file with annotations
    :return: YouTube video code, list with events
    """
    annotations = json_broken_file_to_dict(filename)
    video_code = annotations['videoURL']
    events = events_dict_to_list(annotations)
    return video_code, events


def process_annotation_files():
    """
    Processes all annotation's files from directory specified in config
    :return: dict containing annotated videos with corresponding list with sorted events
    """
    videos = {}

    for json_file in os.listdir(config['input_dir']):
        (video_code, events) = process_annotation_file(f"{config['input_dir']}/{json_file}")

        if video_code not in videos:
            videos[video_code] = []

        videos[video_code].extend(events)

    for key, value in videos.items():
        videos[key] = sorted(value, key=lambda annotation: float(annotation['startTime']))

    return videos


def above_max_fragment_size(annotation):
    return float(annotation['endTime']) - float(annotation['startTime']) > config['max_fragment_size']


def merge_annotations(annotations):
    """
    Merge annotations for a single video file, based on acceptance_threshold, max_fragment_size and match_labels
    :param annotations: list with a single video file annotations
    :return: list of merged annotations
    """
    annotators_list = list(set([annotation['nickname'] for annotation in annotations
                                if above_max_fragment_size(annotation)]))
    annotators_count = len(annotators_list)

    if annotators_count == 0:
        return []

    merged_annotations = [
        {
            'startTime': None,
            'endTime': None,
            'labels': set(),
            'annotators_count': 0,
            'annotators': set()
        }
    ]

    # { startTime, endTime, labels:[], annotators_count, annotators }

    merged_count = 0
    annotations_count = 0
    new_fragment = True
    while annotations_count < len(annotations):
        annotation = annotations[annotations_count]
        if above_max_fragment_size(annotation):
            annotations_count += 1
            continue

        if new_fragment:
            merged_annotations[merged_count]['startTime'] = float(annotation['startTime'])
            merged_annotations[merged_count]['endTime'] = float(annotation['endTime'])
            merged_annotations[merged_count]['labels'].add(annotation['label'])
            merged_annotations[merged_count]['annotators'].add(annotation['nickname'])
            new_fragment = False
        else:
            # print(f"{merged_annotations[merged_count]['endTime']} < {float(annotation['startTime'])}")
            # print(merged_annotations[merged_count]['endTime'] < float(annotation['startTime']))
            if merged_annotations[merged_count]['endTime'] > float(annotation['startTime']):
                merged_annotations[merged_count]['endTime'] = float(annotation['endTime'])
                merged_annotations[merged_count]['labels'].add(annotation['label'])
                merged_annotations[merged_count]['annotators'].add(annotation['nickname'])
            else:
                agreement_ratio = (len(merged_annotations[merged_count]['annotators'])/annotators_count)
                if agreement_ratio >= config['acceptance_threshold']:
                    merged_annotations[merged_count]['annotators_count'] = len(merged_annotations[merged_count]['annotators'])
                    merged_annotations[merged_count]['labels'] = list(merged_annotations[merged_count]['labels'])
                    merged_annotations[merged_count]['annotators'] = list(merged_annotations[merged_count]['annotators'])
                    merged_count += 1
                else:
                    merged_annotations.pop()
                merged_annotations.append(
                    {
                        'startTime': float(annotation['startTime']),
                        'endTime': float(annotation['endTime']),
                        'labels': set([annotation['label']]),
                        'annotators_count': 0,
                        'annotators': set([annotation['nickname']])
                    }
                )
        annotations_count += 1

    agreement_ratio = (len(merged_annotations[merged_count]['annotators']) / annotators_count)

    if agreement_ratio >= config['acceptance_threshold']:
        merged_annotations[merged_count]['annotators_count'] = len(merged_annotations[merged_count]['annotators'])
        merged_annotations[merged_count]['labels'] = list(merged_annotations[merged_count]['labels'])
        merged_annotations[merged_count]['annotators'] = list(merged_annotations[merged_count]['annotators'])
        merged_count += 1
    else:
        merged_annotations.pop()

    return merged_annotations


def merge_videos_annotations(annotations):
    """
    Merge annotations for all video files
    :param annotations: dict with annotations for all video files
    :return: videos dict with merged annotations
    """
    merged_videos_annotations = []
    for key, value in annotations.items():
        merged_videos_annotations.append({'video_code': key, 'annotations': merge_annotations(value)})

    return merged_videos_annotations


config = json_file_to_dict(config_filename)
parse_options()

videos_annotations = process_annotation_files()

if config['annotations_only']:
    dict_to_json_file(videos_annotations)
    exit(0)

dict_to_json_file(merge_videos_annotations(videos_annotations))
