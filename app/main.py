from fastapi import FastAPI
from app.api.api import api_router
from app.db.models import Base
from app.db.session import engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leads API")

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 