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
    """Extract unique labels and all fragments from JSON data."""
    unique_labels = set()
    fragments = []
    
    for video in data:
        for annotation in video['annotations']:
            fragments.append({
                'label': annotation['labels'][0],  # Assume single label per fragment
                'annotators_count': annotation['annotators_count'],
                'annotators': annotation['annotators']
            })
            unique_labels.add(annotation['labels'][0])
    
    return sorted(list(unique_labels)), fragments

def create_rating_matrix(fragments, labels, annotators):
    """Create rating matrix for Fleiss' Kappa."""
    n_fragments = len(fragments)
    n_labels = len(labels)
    label_to_index = {label: i for i, label in enumerate(labels)}
    matrix = np.zeros((n_fragments, n_labels), dtype=int)
    
    for i, fragment in enumerate(fragments):
        label = fragment['label']
        count = fragment['annotators_count']
        if label in label_to_index:
            matrix[i, label_to_index[label]] = count
    
    return matrix

def calculate_fleiss_kappa(matrix, n_annotators):
    """Calculate Fleiss' Kappa from the rating matrix."""
    n_fragments, n_labels = matrix.shape
    if n_fragments == 0:
        return None
    
    # Observed agreement (P_i for each fragment)
    P_i = np.zeros(n_fragments)
    for i in range(n_fragments):
        sum_squares = np.sum(matrix[i] * (matrix[i] - 1))
        P_i[i] = sum_squares / (n_annotators * (n_annotators - 1)) if n_annotators > 1 else 0
    
    P_bar = np.mean(P_i)
    
    # Expected agreement (P_e)
    total_ratings = np.sum(matrix)
    if total_ratings == 0:
        return None
    p_j = np.sum(matrix, axis=0) / total_ratings
    P_e = np.sum(p_j ** 2)
    
    # Fleiss' Kappa
    if P_e == 1:  # Avoid division by zero
        return 1.0 if P_bar == 1 else None
    kappa = (P_bar - P_e) / (1 - P_e)
    
    return kappa

def main(file_path="videos_annotations_devemo.json"):
    """Main function to calculate Fleiss' Kappa from JSON file."""
    # Load JSON data
    data = load_json_data(file_path)
    if not data:
        return
    
    # Extract labels and fragments
    labels, fragments = extract_labels_and_fragments(data)
    if not fragments:
        print("No fragments found in the data.")
        return
    
    # Define annotators
    annotators = ['duygun', 'michal', 'szymon']
    n_annotators = len(annotators)
    
    # Create rating matrix
    rating_matrix = create_rating_matrix(fragments, labels, annotators)
    
    # Calculate Fleiss' Kappa
    kappa = calculate_fleiss_kappa(rating_matrix, n_annotators)
    
    if kappa is not None:
        print(f"Fleiss' Kappa: {kappa:.3f}")
        print("Interpretation:")
        if kappa < 0:
            print("Poor agreement")
        elif kappa <= 0.20:
            print("Slight agreement")
        elif kappa <= 0.40:
            print("Fair agreement")
        elif kappa <= 0.60:
            print("Moderate agreement")
        elif kappa <= 0.80:
            print("Substantial agreement")
        else:
            print("Almost perfect agreement")
    else:
        print("Unable to calculate Kappa (e.g., no ratings or invalid data).")
    
    # Print label distribution for reference
    print("\nLabel Distribution:")
    label_counts = {label: 0 for label in labels}
    for fragment in fragments:
        label_counts[fragment['label']] += fragment['annotators_count']
    for label, count in label_counts.items():
        print(f"{label}: {count} annotator assignments")

if __name__ == "__main__":
    main()