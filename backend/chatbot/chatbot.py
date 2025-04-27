import json
import os
import torch
from sentence_transformers import SentenceTransformer, util

# File path for FAQ dataset
dataset_path = "project_dork_faq.json"

# Load and validate dataset
def load_faq_data(path):
    """Loads the FAQ dataset and ensures it contains valid 'question' and 'answer' pairs."""
    if not os.path.exists(path):
        print(f"Error: FAQ dataset '{path}' not found.")
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        if not isinstance(data, list) or not all("question" in item and "answer" in item for item in data):
            print("Error: Invalid JSON format. Expected a list of {'question': ..., 'answer': ...}")
            return []
        
        return data
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []

# Preprocess text for better matching
def normalize_text(text):
    """Lowercases text and removes extra spaces to improve semantic similarity matching."""
    return " ".join(text.lower().strip().split())

# Load dataset
faq_data = load_faq_data(dataset_path)
questions = [normalize_text(item["question"]) for item in faq_data]
answers = [item["answer"] for item in faq_data]

# Load Sentence Transformer model for semantic search
model = SentenceTransformer("all-MiniLM-L6-v2")
question_embeddings = model.encode(questions, convert_to_tensor=True) if faq_data else None

# Chatbot function
def chat(query: str, threshold=0.5):
    """
    Handles user queries and returns the best matching answer.
    If confidence is below the threshold, returns a default response.
    """
    if not faq_data or question_embeddings is None:
        return {"query": query, "response": "⚠️ Error: FAQ data not available."}

    query = normalize_text(query)
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Compute similarity scores
    similarities = util.pytorch_cos_sim(query_embedding, question_embeddings)[0]
    best_match_idx = similarities.argmax().item()
    confidence = similarities[best_match_idx].item()

    # If similarity is too low, return a fallback response
    if confidence < threshold:
        return {"query": query, "response": "❓ I'm not sure about that. Could you rephrase or ask something else?"}

    return {"query": query, "response": answers[best_match_idx]}

# Interactive chatbot loop
if __name__ == "__main__":
    print("💬 Project Dork Chatbot is running. Type 'exit' or 'quit' to stop.")
    
    conversation_history = []  # Store previous conversations

    while True:
        user_query = input("You: ").strip()
        
        if user_query.lower() in ["exit", "quit"]:
            print("🚪 Exiting chatbot.")
            break
        
        # Get chatbot response
        reply = chat(user_query)
        print("Bot:", reply["response"])
        
        # Store conversation history
        conversation_history.append({"user": user_query, "bot": reply["response"]})

        # Log the conversation
        with open("chat_log.json", "w", encoding="utf-8") as log_file:
            json.dump(conversation_history, log_file, indent=4, ensure_ascii=False)
