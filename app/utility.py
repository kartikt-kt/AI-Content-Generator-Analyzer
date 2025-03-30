import os 
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from . import models, crud
import threading
import requests
import json
import time

load_dotenv()

# API URLs for different models
GENERATION_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-alpha"
SENTIMENT_API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
READABILITY_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

#Define a semaphore to limit the number of concurrent API calls
semaphore = threading.Semaphore(10)

def query(payload, api_url):
    # Try up to 3 times with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload)
            print(f"API Response Status: {response.status_code}")  # Debug print
            print(f"API Response: {response.text}")  # Debug print
            
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # If the model is loading, wait and retry
            if response.status_code == 503:
                wait_time = (2 ** attempt) * 2  # Exponential backoff: 2, 4, 8 seconds
                time.sleep(wait_time)
                continue
                
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {str(e)}")  # Debug print
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"API request failed: {str(e)}")
            wait_time = (2 ** attempt) * 2
            time.sleep(wait_time)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {str(e)}")  # Debug print
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"Failed to parse API response: {str(e)}")
            wait_time = (2 ** attempt) * 2
            time.sleep(wait_time)

def generate_content(db: Session, topic: str) -> str:
    with semaphore:
        try:
            # Get or create search term
            search_term = crud.get_search_term(db, topic)
            if not search_term:
                search_term = crud.create_search_term(db, topic)
            
            # Construct the prompt in Zephyr's expected format
            prompt = f"""<|system|>
You are a knowledgeable assistant that writes comprehensive, well-structured articles. 
Your articles should be informative, engaging, and include relevant details and examples.

<|user|>
Write a detailed article about {topic}. The article should include:
1. A clear introduction explaining what {topic} is
2. Main concepts and key points about {topic}
3. Current developments and real-world applications
4. Future implications and potential impact
5. A conclusion summarizing the key points

Make it engaging and informative while maintaining a professional tone.

<|assistant|>"""
            
            response = query({
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "do_sample": True,
                    "return_full_text": False
                }
            }, GENERATION_API_URL)
            
            # Handle different response formats
            if isinstance(response, list) and len(response) > 0:
                if 'generated_text' in response[0]:
                    generated_text = response[0]['generated_text'].strip()
                elif 'content' in response[0]:
                    generated_text = response[0]['content'].strip()
                else:
                    generated_text = str(response[0]).strip()
            elif isinstance(response, dict):
                if 'generated_text' in response:
                    generated_text = response['generated_text'].strip()
                elif 'content' in response:
                    generated_text = response['content'].strip()
                else:
                    generated_text = str(response).strip()
            else:
                generated_text = str(response).strip()
            
            if not generated_text:
                raise Exception("No content was generated")
                
            crud.create_generated_content(db, generated_text, search_term.id)
            return generated_text
        except Exception as e:
            error_msg = str(e)
            if "loading" in error_msg.lower():
                return "The model is still loading. Please try again in a few seconds."
            return f"Error generating content: {error_msg}"

def analyze_content(db: Session, content: str):
    with semaphore:
        try:
            # Create a search term for the content being analyzed
            search_term = crud.create_search_term(db, content)
            
            # Get readability score
            try:
                readability = get_readability_score(content)
                print(f"Readability result: {readability}")  # Debug print
            except Exception as e:
                print(f"Readability analysis error: {str(e)}")
                readability = "Unable to analyze readability"
            
            # Get sentiment analysis
            try:
                sentiment = get_sentiment_analysis(content)
                print(f"Sentiment result: {sentiment}")  # Debug print
            except Exception as e:
                print(f"Sentiment analysis error: {str(e)}")
                sentiment = "Unable to analyze sentiment"
            
            # Create sentiment analysis record
            try:
                crud.create_sentiment_analysis(db, readability, sentiment, search_term.id)
            except Exception as e:
                print(f"Database error: {str(e)}")
            
            return {
                "readability": readability,
                "sentiment": sentiment
            }
        except Exception as e:
            print(f"General analysis error: {str(e)}")
            raise Exception(f"Error analyzing content: {str(e)}")

def get_readability_score(content: str) -> str:
    try:
        # Simple readability analysis based on text characteristics
        words = content.split()
        sentences = content.split('.')
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Calculate readability score (1-10)
        score = 10  # Start with highest score
        
        # Penalize for long words
        if avg_word_length > 6:
            score -= 2
        elif avg_word_length > 5:
            score -= 1
            
        # Penalize for long sentences
        if avg_sentence_length > 20:
            score -= 2
        elif avg_sentence_length > 15:
            score -= 1
            
        # Penalize for complex words (words with more than 2 syllables)
        complex_words = sum(1 for word in words if len(word) > 8)
        if complex_words > len(words) * 0.2:  # More than 20% complex words
            score -= 2
        elif complex_words > len(words) * 0.1:  # More than 10% complex words
            score -= 1
            
        # Ensure score stays within 1-10 range
        score = max(1, min(10, score))
        
        # Convert score to readability level
        if score >= 8:
            return "Easy to read"
        elif score >= 5:
            return "Moderate difficulty"
        else:
            return "Difficult to read"
            
    except Exception as e:
        print(f"Readability analysis error: {str(e)}")  # Debug print
        return "Unable to analyze readability"

def get_sentiment_analysis(content: str) -> str:
    try:
        # Truncate content if too long (most sentiment models have token limits)
        max_length = 512
        if len(content) > max_length:
            content = content[:max_length] + "..."
            
        response = query({
            "inputs": content
        }, SENTIMENT_API_URL)
        
        print(f"Sentiment API response: {response}")  # Debug print
        
        if isinstance(response, list) and len(response) > 0 and len(response[0]) > 0:
            # The model returns a list of sentiment labels with scores
            sentiments = response[0]
            # Get the highest scored sentiment
            highest_sentiment = max(sentiments, key=lambda x: x['score'])
            label = highest_sentiment['label'].upper()
            score = highest_sentiment['score']
            
            # Convert label to sentiment with confidence threshold
            if score < 0.6:  # If confidence is low, consider it neutral
                return "Neutral"
            elif label == 'POSITIVE':
                return "Positive"
            elif label == 'NEGATIVE':
                return "Negative"
            else:
                return "Neutral"
        return "Neutral"
    except Exception as e:
        print(f"Sentiment analysis error: {str(e)}")  # Debug print
        return "Unable to analyze sentiment"