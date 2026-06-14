import json
from pathlib import Path
from collections import Counter

DATASET_FILE = Path("data/curated/iks_instruction_dataset.jsonl")

def validate():
    if not DATASET_FILE.exists():
        print(f"Dataset file {DATASET_FILE} does not exist.")
        return

    total_pairs = 0
    valid_pairs = 0
    errors = 0
    
    # We can try to infer categories using simple keyword matching, 
    # but for true categorisation we'd need a classifier.
    # We will do a basic keyword match to give rough estimates.
    domain_counts = Counter()
    
    # User's specified target distribution
    target_distribution = {
        "Temple Architecture & Sacred Spaces":  12.0,
        "Classical Music & Ragas":              13.0,
        "Classical Dance & Performing Arts":    10.0,
        "Mythology & Epic Literature":          15.0,
        "Philosophy & Untranslatable Concepts": 13.0,
        "Festivals & Living Traditions":        10.0,
        "Mathematics & Science":                 8.0,
        "Textiles, Craft & Material Culture":    7.0,
        "Medicine, Yoga & Ayurveda":             7.0,
        "Sacred Geography & Pilgrimage":         5.0,
    }
    
    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            total_pairs += 1
            try:
                item = json.loads(line)
                # Check ShareGPT format
                if "conversations" not in item:
                    print(f"Line {i+1}: Missing 'conversations' key.")
                    errors += 1
                    continue
                
                convs = item["conversations"]
                if len(convs) != 2:
                    print(f"Line {i+1}: Expected exactly 2 turns in conversation.")
                    errors += 1
                    continue
                    
                if convs[0]["from"] != "human" or convs[1]["from"] != "gpt":
                    print(f"Line {i+1}: Roles should be 'human' and 'gpt'.")
                    errors += 1
                    continue
                    
                valid_pairs += 1
                
                # Track domains if explicitly output by the new script format
                if "domain" in item and item["domain"]:
                    domain_counts[item["domain"]] += 1
                else:
                    domain_counts["Unspecified"] += 1
                
            except json.JSONDecodeError:
                print(f"Line {i+1}: Invalid JSON.")
                errors += 1

    print("\n" + "="*40)
    print("Dataset Validation Report")
    print("="*40)
    print(f"Total entries processed: {total_pairs}")
    print(f"Valid ShareGPT pairs:  {valid_pairs}")
    print(f"Errors found:          {errors}")
    
    print("\nDomain Distribution Estimate vs Targets:")
    for domain, count in domain_counts.most_common():
        pct = (count / total_pairs) * 100 if total_pairs > 0 else 0
        target = target_distribution.get(domain, 0.0)
        target_str = f" (Target: {target}%)" if target > 0 else " (No specific target)"
        print(f"  {domain}: {count} ({pct:.1f}%){target_str}")

if __name__ == "__main__":
    validate()
