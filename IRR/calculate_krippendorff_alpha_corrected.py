import json
import numpy as np

def load_json_data(file_path):
    """Load JSON data from the specified file path."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from {file_path}.")
        return None

def extract_labels_and_fragments(data):
    """Extract unique labels, annotators, and fragments from JSON data."""
    unique_labels = set()
    all_annotators = set()
    fragments = []
    
    for video in data:
        for annotation in video['annotations']:
            fragments.append({
                'label': annotation['labels'][0],  # Assume single label per fragment
                'annotators': annotation['annotators']
            })
            unique_labels.add(annotation['labels'][0])
            all_annotators.update(annotation['annotators'])
    
    return sorted(list(unique_labels)), sorted(list(all_annotators)), fragments

def create_rating_matrix(fragments, labels, annotators):
    """Create rating matrix for Krippendorff's Alpha."""
    n_fragments = len(fragments)
    n_annotators = len(annotators)
    label_to_index = {label: i for i, label in enumerate(labels)}
    annotator_to_index = {annotator: i for i, annotator in enumerate(annotators)}
    
    # Matrix: rows = fragments, columns = annotators, values = label indices or NaN
    matrix = np.full((n_fragments, n_annotators), np.nan)
    
    for i, fragment in enumerate(fragments):
        label_idx = label_to_index[fragment['label']]
        for annotator in fragment['annotators']:
            matrix[i, annotator_to_index[annotator]] = label_idx
    
    return matrix, label_to_index

def calculate_krippendorff_alpha(matrix, n_labels):
    """Calculate Krippendorff's Alpha for nominal data."""
    n_fragments, n_annotators = matrix.shape
    
    # Treat NaN as a "missing" category
    n_categories = n_labels + 1  # Labels + missing
    missing_idx = n_labels
    
    # Replace NaN with missing category index
    working_matrix = np.where(np.isnan(matrix), missing_idx, matrix)
    
    # Build coincidence matrix
    coincidence = np.zeros((n_categories, n_categories))
    for i in range(n_fragments):
        ratings = working_matrix[i]
        # Count all possible pairs of ratings
        for j in range(n_annotators):
            for k in range(j + 1, n_annotators):
                v1, v2 = int(ratings[j]), int(ratings[k])
                coincidence[v1, v2] += 1
                coincidence[v2, v1] += 1  # Symmetric matrix
    
    # Observed disagreement (D_o)
    observed_disagreement = 0
    for i in range(n_categories):
        for j in range(i + 1, n_categories):
            # Count disagreements only if at least one is a valid label
            if i != missing_idx or j != missing_idx:
                observed_disagreement += coincidence[i, j]
    
    # Total pairs
    total_pairs = n_fragments * n_annotators * (n_annotators - 1) / 2
    if total_pairs == 0:
        return None
    
    D_o = observed_disagreement / total_pairs if total_pairs > 0 else 0
    
    # Expected disagreement (D_e)
    value_counts = np.zeros(n_categories)
    for i in range(n_fragments):
        ratings = working_matrix[i]
        unique, counts = np.unique(ratings, return_counts=True)
        for v, c in zip(unique, counts):
            value_counts[int(v)] += c
    
    total_ratings = np.sum(value_counts)
    if total_ratings == 0:
        return None
    p_j = value_counts / total_ratings
    D_e = 0
    for i in range(n_categories):
        for j in range(i + 1, n_categories):
            # Count expected disagreements only if at least one is a valid label
            if i != missing_idx or j != missing_idx:
                D_e += p_j[i] * p_j[j]
    
    # Krippendorff's Alpha
    if D_e == 0:
        return 1.0 if D_o == 0 else None
    alpha = 1 - (D_o / (2 * D_e))  # Factor of 2 for nominal metric
    
    return alpha

def main(file_path="videos_annotations_devemo.json"):
    """Main function to calculate Krippendorff's Alpha from JSON file."""
    # Load JSON data
    data = load_json_data(file_path)
    if not data:
        return
    
    # Extract labels, annotators, and fragments
    labels, annotators, fragments = extract_labels_and_fragments(data)
    if not fragments:
        print("No fragments found in the data.")
        return
    
    # Create rating matrix
    rating_matrix, label_to_index = create_rating_matrix(fragments, labels, annotators)
    
    # Calculate Krippendorff's Alpha
    alpha = calculate_krippendorff_alpha(rating_matrix, len(labels))
    
    if alpha is not None:
        print(f"Krippendorff's Alpha: {alpha:.3f}")
        print("Interpretation:")
        if alpha < 0:
            print("Poor agreement")
        elif alpha <= 0.2:
            print("Slight agreement")
        elif alpha <= 0.4:
            print("Fair agreement")
        elif alpha <= 0.6:
            print("Moderate agreement")
        elif alpha <= 0.8:
            print("Significant agreement")
        else:
            print("Almost perfect agreement")
    else:
        print("Unable to calculate Alpha (e.g., no valid ratings or insufficient data).")
    
    # Print label distribution for reference
    print("\nLabel Distribution:")
    label_counts = {label: 0 for label in labels}
    for fragment in fragments:
        label_counts[fragment['label']] += len(fragment['annotators'])
    for label, count in label_counts.items():
        print(f"{label}: {count} annotator assignments")

if __name__ == "__main__":
    main()