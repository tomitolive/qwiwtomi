#!/usr/bin/env python3
import json
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_PATH, 'data', 'content_index.json')

def main():
    # Read the current index
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    # Sort by timestamp (descending)
    sorted_index = sorted(index, key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # Write back
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted_index, f, ensure_ascii=False, indent=2)
    
    print(f"Sorted {len(sorted_index)} items by timestamp (descending)")
    print(f"Top 5 items:")
    for i, item in enumerate(sorted_index[:5]):
        print(f"  {i+1}. {item.get('title', 'N/A')} - timestamp: {item.get('timestamp', 0)}")

if __name__ == '__main__':
    main()
