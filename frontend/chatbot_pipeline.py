from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
import os
import torch
import json


# Database setup
DATABASE_URL = "postgresql://dork_user:securepassword@localhost:1234/project_dork"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Define the FAQ model
class FAQ(Base):
    __tablename__ = "faq"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

# Define the Chat History model
class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatbotPipeline:
    def __init__(self, user_id):
        """Initialize chatbot by loading FAQ data from the database and SentenceTransformer model."""
        self.session = Session()
        self.user_id = user_id
        self.faq_data = self.load_faq_data()
        self.questions, self.answers = self.process_faq_data()
        self.model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        self.question_embeddings = self.model.encode(self.questions, convert_to_tensor=True) if self.faq_data else None

    def load_faq_data(self):
        """Loads the FAQ dataset from the database."""
        faqs = self.session.query(FAQ).all()
        return [{"question": faq.question, "answer": faq.answer} for faq in faqs]

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
            response = "❓ I'm not sure about that. Could you rephrase or ask something else?"
        else:
            response = self.answers[best_match_idx]

        # Save the chat history to the database
        self.save_chat_history(query, response)

        return {"query": query, "response": response}

    def save_chat_history(self, query, response):
        """Saves the chat history to the database."""
        chat = ChatHistory(user_id=self.user_id, query=query, response=response)
        self.session.add(chat)
        self.session.commit()

    def clear_chat_history(self):
        """Clears the chat history for the current user."""
        self.session.query(ChatHistory).filter_by(user_id=self.user_id).delete()
        self.session.commit()

# Create tables if they don't exist
Base.metadata.create_all(engine)