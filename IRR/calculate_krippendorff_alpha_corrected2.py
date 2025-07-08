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
                'label': annotation['labels'][0],
                'annotators_count': annotation['annotators_count'],
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
    
    matrix = np.full((n_fragments, n_annotators), np.nan)
    
    for i, fragment in enumerate(fragments):
        label_idx = label_to_index[fragment['label']]
        for annotator in fragment['annotators']:
            matrix[i, annotator_to_index[annotator]] = label_idx
    
    return matrix, label_to_index

def calculate_krippendorff_alpha(matrix, n_labels, labels):
    """Calculate Krippendorff's Alpha for nominal data with debugging."""
    n_fragments, n_annotators = matrix.shape
    
    # Count valid ratings per fragment
    valid_ratings = np.sum(~np.isnan(matrix), axis=1)
    
    # Observed agreement (like Fleiss' P_bar)
    P_i = np.zeros(n_fragments)
    for i in range(n_fragments):
        n_valid = valid_ratings[i]
        if n_valid >= 2:
            P_i[i] = (n_valid * (n_valid - 1) / 2) / (n_annotators * (n_annotators - 1) / 2)
        else:
            P_i[i] = 0  # No agreement possible with <2 ratings
    
    P_bar = np.mean(P_i)
    
    # Expected agreement
    value_counts = np.zeros(n_labels)
    for i in range(n_fragments):
        ratings = matrix[i]
        valid_ratings_values = ratings[~np.isnan(ratings)]
        unique, counts = np.unique(valid_ratings_values, return_counts=True)
        for v, c in zip(unique, counts):
            value_counts[int(v)] += c
    
    total_ratings = np.sum(value_counts)
    if total_ratings == 0:
        return None
    p_j = value_counts / total_ratings
    P_e = np.sum(p_j ** 2)
    
    # Debugging output
    print("\nKrippendorff Debugging:")
    print(f"Total Fragments: {n_fragments}")
    print(f"Total Ratings: {total_ratings}")
    print(f"Observed Agreement (P_bar): {P_bar:.3f}")
    print(f"Expected Agreement (P_e): {P_e:.3f}")
    print(f"Category Counts: {value_counts}")
    print(f"Category Proportions (p_j): {p_j}")
    
    # Krippendorff's Alpha (using Fleiss-like formula for consistency)
    if P_e == 1:
        return 1.0 if P_bar == 1 else None
    alpha = (P_bar - P_e) / (1 - P_e)
    
    return alpha

def main(file_path="videos_annotations_devemo.json"):
    """Main function to calculate Krippendorff's Alpha from JSON file."""
    data = load_json_data(file_path)
    if not data:
        return
    
    labels, annotators, fragments = extract_labels_and_fragments(data)
    if not fragments:
        print("No fragments found in the data.")
        return
    
    rating_matrix, label_to_index = create_rating_matrix(fragments, labels, annotators)
    
    alpha = calculate_krippendorff_alpha(rating_matrix, len(labels), labels)
    
    if alpha is not None:
        print(f"\nKrippendorff's Alpha: {alpha:.3f}")
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
    
    print("\nLabel Distribution:")
    label_counts = {label: 0 for label in labels}
    for fragment in fragments:
        label_counts[fragment['label']] += fragment['annotators_count']
    for label, count in label_counts.items():
        print(f"{label}: {count} annotator assignments")

if __name__ == "__main__":
    main()