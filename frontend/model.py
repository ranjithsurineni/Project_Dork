import re
import nltk
from nltk.corpus import stopwords

# Ensure the stopwords resource is downloaded
try:
    nltk.data.find("corpora/stopwords.zip")
except LookupError:
    nltk.download("stopwords")


class DorkQueryGenerator:
    def __init__(self):
        self.file_types = {
            "pdf": "filetype:pdf", "doc": "filetype:doc", "docx": "filetype:docx",
            "xls": "filetype:xls", "xlsx": "filetype:xlsx", "txt": "filetype:txt",
            "ppt": "filetype:ppt", "pptx": "filetype:pptx", "csv": "filetype:csv"
        }
        self.websites = {
            "youtube": "site:youtube.com", "github": "site:github.com",
            "drive": "site:drive.google.com", "linkedin": "site:linkedin.com",
            "reddit": "site:reddit.com", "stackoverflow": "site:stackoverflow.com",
            "gmail": "site:gmail.com", "instagram": "site:instagram.com"
        }
        self.locations = {
            "new york": "location:New York", "san francisco": "location:San Francisco",
            "london": "location:London", "paris": "location:Paris",
            "mumbai": "location:Mumbai", "delhi": "location:Delhi",
            "bangalore": "location:Bangalore", "hyderabad": "location:Hyderabad",
            "chennai": "location:Chennai", "kolkata": "location:Kolkata",
            "pune": "location:Pune", "jaipur": "location:Jaipur",
            "ahmedabad": "location:Ahmedabad", "lucknow": "location:Lucknow",
            "surat": "location:Surat"
        }
        self.operators = {
            "site": "site:", "filetype": "filetype:", "intitle": "intitle:",
            "link": "link:", "intext": "intext:", "inurl": "inurl:"
        }
        self.stop_words = set(stopwords.words("english"))

    def generate_dork_query(self, user_input):
        categorized_parts = {"site": [], "filetype": [], "location": [], "operator": [], "text": []}

        # Check for multi-word locations first
        for location in self.locations:
            if location in user_input.lower():
                categorized_parts["location"].append(f'"{self.locations[location]}"')
                user_input = re.sub(rf"\b{re.escape(location)}\b", "", user_input, flags=re.IGNORECASE)

        # Split the remaining input into words
        words = [re.sub(r"[^\w\s]", "", word.strip().lower()) for word in user_input.split() if word not in self.stop_words]

        for word in words:
            if word in self.websites:
                categorized_parts["site"].append(self.websites[word])
            elif word in self.file_types:
                categorized_parts["filetype"].append(self.file_types[word])
            elif word in self.locations:
                categorized_parts["location"].append(f'"{self.locations[word]}"')
            elif word in self.operators:
                categorized_parts["operator"].append(self.operators[word])
            else:
                categorized_parts["text"].append(f'"{word}"')

        # Combine all parts into a single query
        query_parts = []
        for key in ["site", "filetype", "location", "operator", "text"]:
            query_parts.extend(categorized_parts[key])

        return " ".join(query_parts)