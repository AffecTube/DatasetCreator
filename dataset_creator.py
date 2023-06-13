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


config = json_file_to_dict(config_filename)
parse_options()

videos_annotations = process_annotation_files()

if config['annotations_only']:
    dict_to_json_file(videos_annotations)
    exit(0)
