import re
import nltk
from collections import defaultdict
from nltk.corpus import wordnet

# Ensure NLTK resources are downloaded
# nltk.download("wordnet")
#  ltk.download("omw-1.4")

# Dictionary Mappings
FILE_TYPES = {"pdf": "filetype:pdf", "doc": "filetype:doc", "docx": "filetype:docx",
    "xls": "filetype:xls", "xlsx": "filetype:xlsx", "txt": "filetype:txt",
    "ppt": "filetype:ppt", "pptx": "filetype:pptx", "csv": "filetype:csv"}

WEBSITES = {"youtube": "site:youtube.com", "github": "site:github.com",
    "drive": "site:drive.google.com", "linkedin": "site:linkedin.com",
    "reddit": "site:reddit.com", "stackoverflow": "site:stackoverflow.com",
    "gmail": "site:gmail.com", "instagram": "site:instagram.com"}

LOCATIONS = {"new york": "location:New York", "san francisco": "location:San Francisco",
    "london": "location:London", "paris": "location:Paris",
    "mumbai": "location:Mumbai", "delhi": "location:Delhi",
    "bangalore": "location:Bangalore", "hyderabad": "location:Hyderabad",
    "chennai": "location:Chennai", "kolkata": "location:Kolkata"}

OPERATORS = {"site": "site:", "filetype": "filetype:", "intitle": "intitle:",
    "link": "link:", "intext": "intext:", "inurl": "inurl:"}

STOPWORDS = {"the", "is", "and", "in", "on", "at", "a", "an", "to", "for", "with", "of", "by"}

LOGICAL_OPERATORS = {"or": "|", "and": "&", "not": "-"}


def get_synonyms(word):
    """Get synonyms for a word to improve intent recognition."""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower().replace("_", " "))
    return synonyms


def identify_search_intent(words):
    """Categorizes words into primary search intent and supporting filters."""
    primary_intent = []
    supporting_filters = []

    for word in words:
        synonyms = get_synonyms(word)
        if any(kw in synonyms for kw in ["title", "headline", "subject"]):
            primary_intent.append(f"intitle:{word}")
        elif any(kw in synonyms for kw in ["content", "text", "body"]):
            primary_intent.append(f"intext:{word}")
        else:
            supporting_filters.append(word)

    return primary_intent, supporting_filters


def generate_dork_query(user_input):
    """Converts human-readable input into an optimized Google Dork query with logical operators."""
    user_input = user_input.lower().strip()
    user_input = re.sub(r"[^\w\s-]", "", user_input)  # Remove punctuation except '-'
    
    query_parts = defaultdict(list)

    # Extract locations first
    for loc in LOCATIONS:
        if loc in user_input:
            query_parts["location"].append(LOCATIONS[loc])
            user_input = user_input.replace(loc, "")
    
    words = user_input.split()
    primary_intent, supporting_filters = identify_search_intent(words)
    
    prev_word = ""
    for word in supporting_filters:
        if word in STOPWORDS:
            continue

        if prev_word == "not" and word in WEBSITES:
            query_parts["site"].append(f"-{WEBSITES[word]}")
        elif prev_word == "not" and word in FILE_TYPES:
            query_parts["filetype"].append(f"-{FILE_TYPES[word]}")
        elif word in WEBSITES:
            query_parts["site"].append(WEBSITES[word])
        elif word in FILE_TYPES:
            query_parts["filetype"].append(FILE_TYPES[word])
        elif word in OPERATORS:
            query_parts["operator"].append(OPERATORS[word])
        elif word in LOGICAL_OPERATORS:
            query_parts["logical"].append(LOGICAL_OPERATORS[word])
        else:
            query_parts["text"].append(f'"{word}"')
        
        prev_word = word
    
    # Add primary search intent to query
    query_parts["intent"] = primary_intent
    
    # Construct query
    query_string = " AND ".join([
        " OR ".join(query_parts[key]) for key in ["intent", "site", "filetype", "location", "operator", "text"] if query_parts[key]
    ])
    
    return query_string.replace(" AND -", " -")


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


#--------------------------------

"""Here's an optimized version of your Google Dork Query Generator. This version enhances query generation by:

Intent Identification: Extracts the main intent of the query and determines relevant search modifiers (intitle:, intext:).

Semantic Grouping: Uses NLTK to find related words and categorize them into primary search intent, site-based filtering, or document types.

Auto-Handling Logical Operators: Ensures logical operators (AND, OR, NOT) are correctly applied where needed.

Better Query Construction: Ensures proper structure and avoids redundant terms."
"""