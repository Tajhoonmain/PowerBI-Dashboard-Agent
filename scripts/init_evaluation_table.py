"""Initialize evaluation_records table."""
from backend.database.connection import init_db, engine, Base
from backend.models.evaluation import EvaluationRecord

# Ensure all models are imported
from backend.models import dataset, dashboard, transformation, evaluation

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ Database tables initialized successfully!")
print("✅ evaluation_records table created/verified")

