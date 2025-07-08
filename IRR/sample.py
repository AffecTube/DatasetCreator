import numpy as np
import krippendorff

# Input data with labels and '0' for missing
reliability_data_str = (
    "Confusion    0    0    0    Happiness    0    Disgust    Confusion    0    0    Surprise    0    Confusion    0    Happiness",  # coder A
    "Confusion    Surprise    Confusion    0    Happiness    0    Disgust    Confusion    Disgust    Confusion    Surprise    0    Confusion    Disgust    0",  # coder B
    "Confusion    0    Confusion    Fear    Happiness    Confusion    Disgust    Confusion    Disgust    Confusion    Surprise    Surprise    Confusion    Disgust    0",  # coder C
)

# Define label mapping
label_map = {
    'Confusion': 0,
    'Happiness': 1,
    'Disgust': 2,
    'Surprise': 3,
    'Fear': 4,
}
# Reverse map if you want to interpret results later
reverse_map = {v: k for k, v in label_map.items()}

# Convert data to numeric, with np.nan for missing
reliability_data = []
for line in reliability_data_str:
    row = [label_map[label] if label in label_map else np.nan for label in line.split()]
    reliability_data.append(row)

# Transpose: krippendorff expects items as columns, coders as rows
data = np.array(reliability_data, dtype=float)
print(data)
# Compute Krippendorff's Alpha
alpha = krippendorff.alpha(reliability_data=data.T, level_of_measurement='nominal')
print(f"Krippendorff's Alpha: {alpha:.3f}")
