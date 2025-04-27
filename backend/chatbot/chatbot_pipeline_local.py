import json
import os
import torch
from sentence_transformers import SentenceTransformer, util

# File path for FAQ dataset
dataset_path = "D:/projects/Project_dork/backend/chatbot/project_dork_faq.json"

class ChatbotPipeline:
    def __init__(self):
        """Initialize chatbot by loading FAQ dataset and SentenceTransformer model."""
        self.faq_data = self.load_faq_data()
        self.questions, self.answers = self.process_faq_data()
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.question_embeddings = self.model.encode(self.questions, convert_to_tensor=True) if self.faq_data else None

    def load_faq_data(self):
        """Loads the FAQ dataset and ensures it contains valid 'question' and 'answer' pairs."""
        if not os.path.exists(dataset_path):
            print(f"Error: FAQ dataset '{dataset_path}' not found.")
            return []
        
        try:
            with open(dataset_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            
            if not isinstance(data, list) or not all("question" in item and "answer" in item for item in data):
                print("Error: Invalid JSON format. Expected a list of {'question': ..., 'answer': ...}")
                return []
            
            return data
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return []

    def process_faq_data(self):
        """Prepares normalized questions and answers from the dataset."""
        questions = [self.normalize_text(item["question"]) for item in self.faq_data]
        answers = [item["answer"] for item in self.faq_data]
        return questions, answers

    @staticmethod
    def normalize_text(text):
        """Lowercases text and removes extra spaces to improve semantic similarity matching."""
        return " ".join(text.lower().strip().split())

    def chat(self, query: str, threshold=0.5):
        """
        Handles user queries and returns the best matching answer.
        If confidence is below the threshold, returns a default response.
        """
        if not self.faq_data or self.question_embeddings is None:
            return {"query": query, "response": "⚠️ Error: FAQ data not available."}

        query = self.normalize_text(query)
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        # Compute similarity scores
        similarities = util.pytorch_cos_sim(query_embedding, self.question_embeddings)[0]
        best_match_idx = similarities.argmax().item()
        confidence = similarities[best_match_idx].item()

        # If similarity is too low, return a fallback response
        if confidence < threshold:
            return {"query": query, "response": "❓ I'm not sure about that. Could you rephrase or ask something else?"}

        return {"query": query, "response": self.answers[best_match_idx]}

# Instantiate the chatbot pipeline
chatbot = ChatbotPipeline()
