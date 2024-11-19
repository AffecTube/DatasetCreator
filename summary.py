import json
from functools import reduce


def json_file_to_dict(filename):
    """
    Reads the JSON file
    :param filename: JSON file name
    :return: Deserialized JSON to dict
    """
    with open(filename, 'r') as file:
        return json.load(file)


config_filename = "config.json"
config = json_file_to_dict(config_filename)

annotations = json_file_to_dict(config['output_filename'])

count = 0
for video in annotations:
    list_a = [x['endTime'] - x['startTime'] for x in video['annotations']]
    count += sum(list_a)
    print(f"{video['video_code']}: {round(sum(list_a),2)}, {video['fragments_count']}")

print(round(count, 2))
