import json
import os

config_filename = "config.json"


def json_file_to_dict(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def json_broken_file_to_dict(filename):
    with open(filename, 'r') as file:
        data = file.read().rstrip().lstrip('"').rstrip('"').replace('\\', '')
    return json.loads(data)


def events_dict_to_list(annotation, annotator_nickname):
    events = []
    for key, value in annotation.items():
        if type(value) is dict:
            value['nickname'] = annotator_nickname
            events.append(value)
    return events


def process_annotation_file(filename):
    annotation = json_broken_file_to_dict(filename)
    annotator_nickname = annotation['nickname']
    video_url = annotation['videoURL']
    events = events_dict_to_list(annotation, annotator_nickname)
    return video_url, events


def process_annotation_files():
    videos = {}

    for json_file in os.listdir(config['input_dir']):
        (video_url, events) = process_annotation_file(f"{config['input_dir']}/{json_file}")

        if video_url not in videos:
            videos[video_url] = []

        videos[video_url].extend(events)
    return videos


config = json_file_to_dict(config_filename)

videos_annotations = process_annotation_files()

for key, value in videos_annotations.items():
    videos_annotations[key] = sorted(value, key=lambda annotation: float(annotation['startTime']))

with open("videos_annotations.json", "w") as fp:
    json.dump(videos_annotations, fp, indent=4)
