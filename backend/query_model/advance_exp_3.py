import re
import nltk
import spacy
import os
from collections import defaultdict
from nltk.corpus import wordnet
from transformers import pipeline

from Data.locations import LOCATIONS
from Data.File_types import FILE_TYPES
from Data.websites import WEBSITES

# Load spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")


# Load Hugging Face summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")



    
# Dictionary Mappings for Websites
# Dictionary Mappings for Websites with Categories





# Logical Operators for Query Construction
LOGICAL_OPERATORS = {"or": "|", "and": "&", "not": "-", "&&": "&", "||": "|",}



def get_synonyms(word):
    """Get synonyms for a word to improve intent recognition."""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower().replace("_", " "))
    return synonyms



def summarize_text(text):
    """Summarize the input text to extract key information."""
    # Skip summarization for very short inputs
    if len(text.split()) < 30:
        return text

    # Dynamically adjust max_length and min_length
    max_length = min(50, len(text.split()))
    min_length = max(25, max_length // 2)

    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]["summary_text"]



def extract_entities(text):
    """Extract entities like locations, organizations, and topics using spaCy."""
    doc = nlp(text)
    entities = {"locations": [], "organizations": [], "topics": []}

    for ent in doc.ents:
        if ent.label_ == "GPE":  # Geopolitical Entity
            entities["locations"].append(ent.text.lower())
        elif ent.label_ in {"ORG", "FAC"}:  # Organizations or Facilities
            entities["organizations"].append(ent.text.lower())
        elif ent.label_ in {"PERSON", "PRODUCT", "EVENT", "NORP"}:  # Topics or related entities
            entities["topics"].append(ent.text.lower())

    # Add additional logic to extract multi-word phrases as topics
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1:  # Consider multi-word phrases
            entities["topics"].append(chunk.text.lower())

    # Check for custom locations
    words = text.lower().split()
    for word in words:
        if word in LOCATIONS and word not in entities["locations"]:
            entities["locations"].append(word)

    return entities


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


def generate_dork_query_from_paragraph(paragraph):
    """Generate a Google Dork query from a paragraph."""
    # Step 1: Summarize the paragraph
    summarized_text = summarize_text(paragraph)

    # Step 2: Extract entities from the summarized text
    entities = extract_entities(summarized_text)
    print("Extracted Entities:", entities)

    # Step 3: Initialize query parts
    query_parts = defaultdict(list)

    # Step 4: Process locations
    for loc in entities["locations"]:
        normalized_loc = loc.lower().strip()
        if normalized_loc in LOCATIONS:
            query_parts["location"].append(LOCATIONS[normalized_loc])
        else:
            print(f"Warning: Location '{normalized_loc}' not found in predefined locations.")
    #print("Available Locations:", LOCATIONS)
    
    # Step 5: Process organizations and topics
    for org in entities["organizations"]:
        if org in WEBSITES:
            query_parts["site"].append(WEBSITES[org])
    for topic in entities["topics"]:
        query_parts["text"].append(f'intext:"{topic}"')

    # Step 6: Detect and prioritize file types based on categories
    words = summarized_text.lower().split()  # Tokenize and convert to lowercase
    detected_file_types = set()

    for file_type, details in FILE_TYPES.items():
        if any(category in words for category in details["category"]):
            detected_file_types.add(details["type"])

    # Prioritize file types (e.g., prefer "pdf" over others if present)
    prioritized_file_types = []
    if "filetype:pdf" in detected_file_types:
        prioritized_file_types.append("filetype:pdf")
    else:
        prioritized_file_types.extend(detected_file_types)

    # Add prioritized file types to the query
    if prioritized_file_types:
        query_parts["filetype"].append(" OR ".join(prioritized_file_types))

    # Step 7: Dynamically include relevant websites
    relevant_websites = []
    for keyword in words:
        for site, site_url in WEBSITES.items():
            if keyword in site:  # Match keyword with website name or category
                relevant_websites.append(site_url)

    # Filter and limit relevant websites
    filtered_websites = set(relevant_websites)  # Remove duplicates
    if len(filtered_websites) > 3:  # Limit to 3 websites
        filtered_websites = list(filtered_websites)[:3]

    # Add relevant websites to the query
    if filtered_websites:
        query_parts["site"].append(f"({' OR '.join(filtered_websites)})")

    # Step 8: Process negations (e.g., "NOT gmail")
    negations = [word for word in words if word.startswith("not") or word.startswith("exclude")]
    for negation in negations:
        negation_word = negation.replace("not", "").replace("exclude", "").strip()
        if negation_word in words:
            words.remove(negation_word)  # Remove the negated word from the list
            query_parts["text"].append(f"-{negation_word}")  # Add to query with negation

    # Step 9: Process remaining words
    primary_intent, supporting_filters = identify_search_intent(words)

    # Add primary search intent to query
    query_parts["intent"] = primary_intent

    # Step 10: Construct the query with grouping
    query_string = " AND ".join([
        f"({ ' OR '.join(query_parts[key]) })" if len(query_parts[key]) > 1 else f"{query_parts[key][0]}"
        for key in ["intent", "site", "filetype", "location", "text"] if query_parts[key]
    ])

    return query_string.replace(" AND -", " -")

#=============================================================================

# Example Usage
print("Usage Instructions:")
print("Example Input: 'resume pdf, github projects, NOT gmail, new york'")
print("Type 'exit' or 'quit' to stop the program.")

while True:
    user_input = input("\nEnter your search text: ").strip()

    # Exit condition
    if user_input.lower() in ["exit", "quit", "c"]:
        print("👋 Exiting the program. Goodbye!")
        break

    if not user_input:
        print("❌ Error: Input cannot be empty.")
        continue

    # Generate the Dork Query
    dork_query = generate_dork_query_from_paragraph(user_input)
    print("\n🔍 Generated Dork Query:")
    print("=" * 50)
    print(f"👉 {dork_query}")
    print("=" * 50)

    # Ask if the user wants to save the query
    if input("Do you want to save the query? (Y/N): ").strip().lower() in ["y", "yes"]:
        with open("dork_query_log.txt", "a") as file:
            file.write(dork_query + "\n")
        print("✅ Query saved!")
    else:
        print("❌ Query not saved.")

#-------------------------------------------------------------------------------------------
