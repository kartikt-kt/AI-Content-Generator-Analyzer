from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models, crud, database, utility, schemas

from .database import engine, SessionLocal
from starlette.concurrency import run_in_threadpool

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})
    
@app.post("/generate/")
async def generate_content(payload: schemas.GeneratePayload, db: Session = Depends(get_db)):
    try:
        generated_text = await run_in_threadpool(utility.generate_content, db, payload.topic)
        return {"generated_text": generated_text, "success": True}
    except Exception as e:
        return {"generated_text": str(e), "success": False}

@app.post("/analyze/")
async def analyze_content(payload: schemas.AnalyzePayload, db: Session = Depends(get_db)):
    try:
        analysis = await run_in_threadpool(utility.analyze_content, db, payload.content)
        if isinstance(analysis, dict):
            return {
                "readability": analysis.get("readability", "Unable to analyze readability"),
                "sentiment": analysis.get("sentiment", "Unable to analyze sentiment"),
                "success": True
            }
        else:
            print(f"Unexpected analysis result type: {type(analysis)}")
            return {
                "readability": "Error analyzing content",
                "sentiment": "Error analyzing content",
                "success": False
            }
    except Exception as e:
        print(f"Analysis endpoint error: {str(e)}")  # Debug print
        return {
            "readability": "Error analyzing content",
            "sentiment": "Error analyzing content",
            "success": False
        }


