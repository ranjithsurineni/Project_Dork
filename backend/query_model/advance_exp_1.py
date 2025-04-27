import re
from collections import defaultdict

# Dictionary Mappings
FILE_TYPES = {
    "pdf": "filetype:pdf", "doc": "filetype:doc", "docx": "filetype:docx",
    "xls": "filetype:xls", "xlsx": "filetype:xlsx", "txt": "filetype:txt",
    "ppt": "filetype:ppt", "pptx": "filetype:pptx", "csv": "filetype:csv"
}

WEBSITES = {
    "youtube": "site:youtube.com", "github": "site:github.com",
    "drive": "site:drive.google.com", "linkedin": "site:linkedin.com",
    "reddit": "site:reddit.com", "stackoverflow": "site:stackoverflow.com",
    "gmail": "site:gmail.com", "instagram": "site:instagram.com"
}

LOCATIONS = {
    "new york": "location:New York", "san francisco": "location:San Francisco",
    "london": "location:London", "paris": "location:Paris",
    "mumbai": "location:Mumbai", "delhi": "location:Delhi",
    "bangalore": "location:Bangalore", "hyderabad": "location:Hyderabad",
    "chennai": "location:Chennai", "kolkata": "location:Kolkata"
}

OPERATORS = {
    "site": "site:", "filetype": "filetype:", "intitle": "intitle:",
    "link": "link:", "intext": "intext:", "inurl": "inurl:"
}

STOPWORDS = {"the", "is", "and", "in", "on", "at", "a", "an", "to", "for", "with", "of", "by"}

LOGICAL_OPERATORS = {"or": "|", "and": "&", "not": "-"}


def generate_dork_query(user_input):
    """Converts human-readable input into an optimized Google Dork query with logical operators."""
    
    user_input = user_input.lower().strip()
    user_input = re.sub(r"[^\w\s-]", "", user_input)  # Remove punctuation except '-'

    query_parts = defaultdict(list)  # Automatically handle missing keys

    # Extract locations first
    for loc in LOCATIONS:
        if loc in user_input:
            query_parts["location"].append(LOCATIONS[loc])
            user_input = user_input.replace(loc, "")  # Remove matched location

    words = user_input.split()
    prev_word = ""

    for word in words:
        if word in STOPWORDS:
            continue  # Skip common words

        if prev_word == "not" and word in WEBSITES:
            query_parts["site"].append(f"-{WEBSITES[word]}")  # Exclude website
        elif prev_word == "not" and word in FILE_TYPES:
            query_parts["filetype"].append(f"-{FILE_TYPES[word]}")  # Exclude file type
        elif word in WEBSITES:
            query_parts["site"].append(WEBSITES[word])
        elif word in FILE_TYPES:
            query_parts["filetype"].append(FILE_TYPES[word])
        elif word in OPERATORS:
            query_parts["operator"].append(OPERATORS[word])
        elif word in LOGICAL_OPERATORS:
            query_parts["logical"].append(LOGICAL_OPERATORS[word])  # Handle AND, OR, NOT
        else:
            query_parts["text"].append(f'"{word}"')  # Wrap general search terms in quotes

        prev_word = word

    # Construct query with logical operators
    query_string = " AND ".join([
        " OR ".join(query_parts[key]) for key in ["site", "filetype", "location", "operator", "text"] if query_parts[key]
    ])

    return query_string.replace(" AND -", " -")  # Remove incorrect AND before NOT


# Example Usage
print("Usage Instructions:")
print("Example Input: 'resume pdf, github projects, NOT gmail, new york'")

user_input = input("Enter your search text: ").strip()

if not user_input:
    print("❌ Error: Input cannot be empty.")
else:
    dork_query = generate_dork_query(user_input)
    print("\n🔍 Generated Dork Query:")
    print("=" * 50)
    print(f"👉 {dork_query}")
    print("=" * 50)

    if input("Do you want to save the query? (Y/N): ").strip().lower() in ["y", "yes"]:
        with open("dork_query_log.txt", "a") as file:
            file.write(dork_query + "\n")
        print("✅ Query saved!")
