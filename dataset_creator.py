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
    """
    Checks if annotation is above max_fragment length
    :param annotation: single annotation
    :return: True if annotation is above max_fragment length, otherwise False
    """
    return float(annotation['endTime']) - float(annotation['startTime']) > config['max_fragment_size']


def merge_annotations_any_label(annotations, annotators_count):
    """
    Merging annotations for a single video file without checking label matches
    :param annotators_count: number of annotators
    :param annotations: list with a single video file annotations
    :return: list of merged annotations
    """
    merged_annotations = [
        {
            'startTime': float(annotations[0]['startTime']),
            'endTime': float(annotations[0]['endTime']),
            'labels': {annotations[0]['label']},
            'annotators_count': 0,
            'annotators': {annotations[0]['nickname']}
        }
    ]

    merged_count = 0
    annotations_count = 1

    while annotations_count < len(annotations):
        annotation = annotations[annotations_count]

        if above_max_fragment_size(annotation):
            annotations_count += 1
            continue

        current_merged = merged_annotations[merged_count]

        if current_merged['endTime'] > float(annotation['startTime']):
            if current_merged['endTime'] < float(annotation['endTime']):
                current_merged['endTime'] = float(annotation['endTime'])
            current_merged['labels'].add(annotation['label'])
            current_merged['annotators'].add(annotation['nickname'])
        else:
            agreement_ratio = len(current_merged['annotators']) / annotators_count

            if agreement_ratio >= config['acceptance_threshold']:
                current_merged['annotators_count'] = len(current_merged['annotators'])
                current_merged['labels'] = list(current_merged['labels'])
                current_merged['annotators'] = list(current_merged['annotators'])
                merged_count += 1
            else:
                merged_annotations.pop()

            merged_annotations.append({
                'startTime': float(annotation['startTime']),
                'endTime': float(annotation['endTime']),
                'labels': {annotation['label']},
                'annotators_count': 0,
                'annotators': {annotation['nickname']}
            })

        annotations_count += 1

    current_merged = merged_annotations[merged_count]
    agreement_ratio = len(current_merged['annotators']) / annotators_count

    if agreement_ratio >= config['acceptance_threshold']:
        current_merged['annotators_count'] = len(current_merged['annotators'])
        current_merged['labels'] = list(current_merged['labels'])
        current_merged['annotators'] = list(current_merged['annotators'])
        merged_count += 1
    else:
        merged_annotations.pop()

    return merged_annotations


def merged_annotation_dict(annotation):
    """
    Returns dict for single annotation
    :param annotation: single annotation
    :return: dict for single annotation
    """
    return {
        'startTime': float(annotation['startTime']),
        'endTime': float(annotation['endTime']),
        'annotators_count': 0,
        'annotators': {annotation['nickname']}
    }


def merge_annotations_match_labels(annotations, annotators_count):
    """
    Merging annotations for a single video file with label matching checks
    :param annotators_count: number of annotators
    :param annotations: list with a single video file annotations
    :return: list of merged annotations
    """

    if annotators_count == 0:
        return []

    temp_merged_annotations = {}
    merged_annotations = []

    for annotation in annotations:
        if above_max_fragment_size(annotation):
            continue

        if annotation['label'] in temp_merged_annotations:
            current_temp_merged = temp_merged_annotations[annotation['label']]

            if current_temp_merged['endTime'] > float(annotation['startTime']):
                if current_temp_merged['endTime'] < float(annotation['endTime']):
                    current_temp_merged['endTime'] = float(annotation['endTime'])
                current_temp_merged['annotators'].add(annotation['nickname'])
            else:
                agreement_ratio = len(current_temp_merged['annotators']) / annotators_count
                if agreement_ratio >= config['acceptance_threshold']:
                    current_temp_merged['annotators_count'] = len(current_temp_merged['annotators'])
                    current_temp_merged['labels'] = list({annotation['label']})
                    current_temp_merged['annotators'] = list(current_temp_merged['annotators'])
                    merged_annotations.append(current_temp_merged)
                temp_merged_annotations[annotation['label']] = merged_annotation_dict(annotation)

        else:
            temp_merged_annotations[annotation['label']] = merged_annotation_dict(annotation)

    for key, value in temp_merged_annotations.items():
        value['labels'] = [key]
        value['annotators_count'] = len(value['annotators'])
        value['annotators'] = list(value['annotators'])

        merged_annotations.append(value)

    return sorted(merged_annotations, key=lambda single_annotation: float(single_annotation['startTime']))


def merge_annotations(annotations):
    """
    Merge annotations for a single video file, based on acceptance_threshold, max_fragment_size and match_labels
    :param annotations: list with a single video file annotations
    :return: list of merged annotations
    """
    annotators_list = list(set(annotation['nickname'] for annotation in annotations
                               if above_max_fragment_size(annotation)))
    annotators_count = len(annotators_list)

    if annotators_count == 0:
        return []

    if config['match_labels']:
        return merge_annotations_match_labels(annotations, annotators_count)
    else:
        return merge_annotations_any_label(annotations, annotators_count)


def merge_videos_annotations(annotations):
    """
    Merge annotations for all video files
    :param annotations: dict with annotations for all video files
    :return: videos dict with merged annotations
    """
    merged_videos_annotations = []
    for key, value in annotations.items():
        merged_annotations = merge_annotations(value)
        merged_videos_annotations.append(
            {'video_code': key, 'fragments_count': len(merged_annotations), 'annotations': merged_annotations})

    return merged_videos_annotations


config = json_file_to_dict(config_filename)
parse_options()

videos_annotations = process_annotation_files()

if config['annotations_only']:
    dict_to_json_file(videos_annotations)
    exit(0)

dict_to_json_file(merge_videos_annotations(videos_annotations))
