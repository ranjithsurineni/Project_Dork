import json
import os

# Filepath to the JSON file
file_path = r"D:\projects\Project_dork\backend\chatbot\project_dork_faq.json"
backup_path = file_path + ".backup"  # Backup file

def normalize_text(text):
    """Normalize text by removing extra spaces and converting to lowercase."""
    return " ".join(text.lower().strip().split())

def remove_duplicate_questions(file_path):
    """Removes duplicate questions and answers from the JSON FAQ file, creating a backup before saving."""
    
    # Load the JSON data from the file
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    if not isinstance(data, list):
        print("Error: The JSON structure must be a list of FAQs.")
        return

    # Create a backup before modifying
    if not os.path.exists(backup_path):
        with open(backup_path, "w", encoding="utf-8") as backup_file:
            json.dump(data, backup_file, indent=4, ensure_ascii=False)
        print(f"Backup created at {backup_path}")

    # Dictionary to track unique questions and answers
    unique_entries = {}
    duplicates = []

    for entry in data:
        if "question" in entry and "answer" in entry:
            normalized_question = normalize_text(entry["question"])
            normalized_answer = normalize_text(entry["answer"])

            key = (normalized_question, normalized_answer)  # Unique key based on question & answer
            
            if key not in unique_entries:
                unique_entries[key] = entry  # Store the first occurrence
            else:
                duplicates.append(entry)  # Store duplicate for logging

    # Convert dictionary values back to a list
    cleaned_data = list(unique_entries.values())

    # Save the cleaned data back to the file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(cleaned_data, file, indent=4, ensure_ascii=False)
    
    print(f"✅ Duplicates removed. Updated data saved to {file_path}")
    print(f"🗑 Removed {len(duplicates)} duplicate entries.")

    # Optionally, save removed duplicates for review
    if duplicates:
        duplicates_path = file_path.replace(".json", "_duplicates.json")
        with open(duplicates_path, "w", encoding="utf-8") as file:
            json.dump(duplicates, file, indent=4, ensure_ascii=False)
        print(f"📁 Removed duplicates saved separately at {duplicates_path}")

# Run the function
remove_duplicate_questions(file_path)
