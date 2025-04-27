import re
import nltk
from nltk.corpus import stopwords

# Ensure the stopwords resource is downloaded
try:
    nltk.data.find("corpora/stopwords.zip")
except LookupError:
    nltk.download("stopwords")


def generate_dork_query(user_input):
    """Converts human-readable input to a Google Dork query."""
    
    # Define mappings for file types and websites
    file_types = {
        "pdf": "filetype:pdf", "doc": "filetype:doc", "docx": "filetype:docx",
        "xls": "filetype:xls", "xlsx": "filetype:xlsx", "txt": "filetype:txt",
        "ppt": "filetype:ppt", "pptx": "filetype:pptx", "csv": "filetype:csv"
    }
    
    websites = {
        "youtube": "site:youtube.com", "github": "site:github.com",
        "drive": "site:drive.google.com", "linkedin": "site:linkedin.com",
        "reddit": "site:reddit.com", "stackoverflow": "site:stackoverflow.com",
        "gmail": "site:gmail.com", "instagram": "site:instagram.com"
    }

    locations = {
        "new york": "location:New York", 
        "san francisco": "location:San Francisco",
        "london": "location:London", 
        "paris": "location:Paris",
        "mumbai": "location:Mumbai", 
        "delhi": "location:Delhi", 
        "bangalore": "location:Bangalore", 
        "hyderabad": "location:Hyderabad", 
        "chennai": "location:Chennai", 
        "kolkata": "location:Kolkata", 
        "pune": "location:Pune", 
        "jaipur": "location:Jaipur", 
        "ahmedabad": "location:Ahmedabad", 
        "lucknow": "location:Lucknow", 
        "surat": "location:Surat"
    }


    operators = {
        "site": "site:", "filetype": "filetype:", "intitle": "intitle:",
        "link": "link:", "intext": "intext:", "inurl": "inurl:"
    }

    # List of stop words to remove
    stop_words = set(stopwords.words("english"))

    # Initialize categorized parts dictionary
    categorized_parts = {"site": [], "filetype": [], "location": [], "operator": [], "text": []}


    #Use re.sub(r"[^\w\s]", "", word) to clean punctuation properly.
    # Split the user input into words and categorize them
    # based on the type of search criteria
    #
    # Convert input text to lowercase and split into words
    # Check for multi-word locations first
    for location in locations:
        if location in user_input.lower():
            categorized_parts["location"].append(f'"{locations[location]}"')
            user_input = user_input.lower().replace(location, "")  # Remove matched location from input

    # Split the remaining input into words
    words = [re.sub(r"[^\w\s]", "", word.strip().lower()) for word in user_input.split() if word not in stop_words]

    for word in words:        # Iterate over each word in the input
        if word in websites:
            categorized_parts["site"].append(websites[word])  # Add website dork
        elif word in file_types:
            categorized_parts["filetype"].append(file_types[word])  # Add file type dork
        elif word in locations:
            categorized_parts["location"].append(f'"{locations[word]}"')  # Add location in quotes
        elif word in operators:
            categorized_parts["operator"].append(operators[word])  # Add operator
        else:
            categorized_parts["text"].append(f'"{word}"')  # Add general terms in quotes

    # Combine all parts into a single query
    query_parts = []
    for key in ["site", "filetype", "location", "operator", "text"]:
        query_parts.extend(categorized_parts[key])

    return " ".join(query_parts)  # Return the formatted dork query

# Example usage
try:
    # Get user input
    print("ℹ️ Usage Instructions:")
    print("You can use the following formats for your search:")
    print("1. Search within a specific website: 'site:github.com machine learning'")
    print("2. Find specific file types: 'filetype:pdf cybersecurity'")
    print("3. Search for pages with specific titles: 'intitle:\"data privacy\"'")
    print("4. Find pages linking to a specific URL: 'link:example.com'")
    print("5. Search for specific text on a webpage: 'intext:\"cyber threat\"'")
    print("6. Combine multiple criteria: 'site:gmail.com hyderabad filetype:pdf software engineering'")
    print("\nExample Input: 'resume pdf, github projects, gmail, new york'")


    user_input = input("Enter your search text: ")
    
    # Validate user input
    if not user_input.strip():
        print("❌ Error: Input cannot be empty. Please provide valid search text.")
        exit()
    
    dork_query = generate_dork_query(user_input)
    print("\n🔍 Generated Dork Query:")
    print("=" * 50)
    print(f"👉 {dork_query}")
    print("=" * 50)

    save_option = input("Do you want to save the query to a file? (Y/N): ").strip().lower()
    if save_option in ["YES", "yes", "Y", "y"]:
        with open("dork_query_log.txt", "a") as file:
            file.write(dork_query + "\n")
        print("✅ Query saved to 'dork_query_log.txt'")
        print("👋 Thank you for using the Dork Generator. Goodbye!")
    elif save_option in ["NO", "no", "N", "n"]:
        print("👋 Thank you for using the Dork Generator. Goodbye!")
    else:
        print("❌ Invalid option. Exiting...")
except Exception as e:
    print(f"❌ An error occurred: {e}")