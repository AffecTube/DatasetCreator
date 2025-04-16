import json
from collections import Counter
from itertools import combinations

# Load the JSON data
with open('videos_annotations_devemo.json', 'r') as f:
    data = json.load(f)

combo_counter = Counter()

for video in data:
    for annotation in video['annotations']:
        annotators = sorted(annotation['annotators'])
        count = len(annotators)

        if count == 1:
            # Count only individual annotations made alone
            combo_counter[annotators[0]] += 1
        elif count == 2:
            # Count only exact pair annotations (not part of a trio)
            key = '+'.join(annotators)
            combo_counter[key] += 1
        elif count == 3:
            # Count only full trio annotations
            key = '+'.join(annotators)
            combo_counter[key] += 1

# Print sorted results
for k in sorted(combo_counter):
    print(f"{k}: {combo_counter[k]}")
