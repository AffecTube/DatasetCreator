import json
import os

config_filename = "config.json"


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


def events_dict_to_list(annotations):
    """
    Process events annotated by single annotator in a single video
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
    Process single annotation file
    :param filename: name of the file with annotations
    :return: YouTube video code, list with events
    """
    annotations = json_broken_file_to_dict(filename)
    video_code = annotations['videoURL']
    events = events_dict_to_list(annotations)
    return video_code, events


def process_annotation_files():
    """
    Process all annotation's files from directory specified in config
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


config = json_file_to_dict(config_filename)

videos_annotations = process_annotation_files()

with open("videos_annotations.json", "w") as fp:
    json.dump(videos_annotations, fp, indent=4)
