import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from database import engine, Base, SessionLocal
from models import User, Appointment, Reminder
import datetime

# Create SQLite tables
Base.metadata.create_all(bind=engine)

def populate_mock_data():
    db = SessionLocal()
    
    # Check if demo user exists
    user = db.query(User).filter(User.email == "patient@demo.com").first()
    if not user:
        user = User(name="Demo Patient", email="patient@demo.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    db.close()
    
    print("Relational database initialized with Demo Patient.")

    # Initialize Vector DB for Doctor Profiles
    print("Initializing Vector DB (Chroma)...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Some mock doctors
    doctors = [
        {"name": "Dr. Alice Smith", "specialty": "Cardiologist", "location": "Building A, Floor 2", "experience": "15 years", "description": "Expert in heart diseases, hypertension, and preventive cardiology."},
        {"name": "Dr. Bob Johnson", "specialty": "Dermatologist", "location": "Building B, Floor 1", "experience": "8 years", "description": "Specializes in skin conditions, acne, eczema, and skin cancer screening."},
        {"name": "Dr. Charlie Brown", "specialty": "General Practitioner", "location": "Building A, Ground Floor", "experience": "20 years", "description": "Provides comprehensive medical care for individuals of all ages."},
        {"name": "Dr. Diana Prince", "specialty": "Neurologist", "location": "Building C, Floor 3", "experience": "12 years", "description": "Treats disorders of the nervous system including migraines, epilepsy, and Parkinson's."},
        {"name": "Dr. Evan Wright", "specialty": "Orthopedic Surgeon", "location": "Building B, Floor 2", "experience": "10 years", "description": "Focuses on injuries and diseases of the musculoskeletal system, including joint replacements."}
    ]
    
    docs = []
    for doc in doctors:
        page_content = f"Doctor Name: {doc['name']}\nSpecialty: {doc['specialty']}\nExperience: {doc['experience']}\nDescription: {doc['description']}"
        metadata = {"name": doc['name'], "specialty": doc['specialty'], "location": doc['location']}
        docs.append(Document(page_content=page_content, metadata=metadata))
        
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    print("Vector DB populated successfully.")

if __name__ == "__main__":
    # Ensure API key is set
    if "GOOGLE_API_KEY" not in os.environ:
        print("WARNING: GOOGLE_API_KEY environment variable is not set. Embedding might fail.")
    populate_mock_data()
