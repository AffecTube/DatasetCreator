import json

config_filename = "config.json"


def json_file_to_dict(filename: str):
    with open(filename) as file:
        return json.load(file)


config = json_file_to_dict(config_filename)

annotation = json_file_to_dict(f"{config['input_dir']}/0adee8d9-2fa4-4e93-a757-29ac442ae977.json")
annotator_nickname = annotation['nickname']
videoURL = annotation['videoURL']

video_annotations = {'videoUrl': videoURL, 'annotations': []}

for key, value in annotation.items():
    if type(value) is dict:
        value.update({'nickname': annotator_nickname})
        print(f"{key} - {value}")
