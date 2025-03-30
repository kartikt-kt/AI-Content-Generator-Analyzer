from sqlalchemy.orm import Session
from . import models, schemas

def get_search_term(db: Session, term: str):
    return db.query(models.SearchTerm).filter(models.SearchTerm.term == term).first()

def create_search_term(db: Session, term: str):
    db_search_term = models.SearchTerm(term=term)
    db.add(db_search_term)
    db.commit()
    db.refresh(db_search_term)
    return db_search_term

def create_generated_content(db: Session, content: str, search_term_id: int):
    db_generated_content = models.GeneratedContent(content=content, search_term_id=search_term_id)
    db.add(db_generated_content)
    db.commit()
    db.refresh(db_generated_content)
    return db_generated_content

def create_sentiment_analysis(db: Session, readability: str, sentiment: str, search_term_id: int):
    db_sentiment = models.SentimentAnalysis(readability=readability, sentiment=sentiment, search_term_id=search_term_id)
    db.add(db_sentiment)
    db.commit()
    db.refresh(db_sentiment)
    return db_sentiment

def get_search_term(db: Session, term: str):
    return db.query(models.SearchTerm).filter(models.SearchTerm.term == term).first()
