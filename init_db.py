from database import Base, engine
from models import ResearchRun

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")