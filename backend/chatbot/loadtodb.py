import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text

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

# Load JSON data into the database
def load_faq_data(json_file):
    session = Session()  # Create a new session
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            for item in data:
                faq = FAQ(question=item["question"], answer=item["answer"])
                session.add(faq)
            session.commit()
            print("FAQ data uploaded successfully!")
    except Exception as e:
        session.rollback()  # Rollback the transaction in case of an error
        print(f"An error occurred: {e}")
    finally:
        session.close()  # Ensure the session is closed

# Run the script
if __name__ == "__main__":
    Base.metadata.create_all(engine)  # Create tables if they don't exist
    load_faq_data("D:/projects/Project_dork/backend/chatbot/project_dork_faq.json")