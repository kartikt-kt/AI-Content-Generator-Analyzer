# AI Content Analyzer

A modern web application that generates and analyzes content using state-of-the-art AI models from Hugging Face. The application provides content generation capabilities along with readability and sentiment analysis features.

## Features

- **Content Generation**: Generate detailed, well-structured articles on any topic using the Zephyr-7B model
- **Content Analysis**:
  - Readability Assessment: Evaluate the complexity of text
  - Sentiment Analysis: Determine the emotional tone of content
- **User-Friendly Interface**:
  - Clean, modern UI design
  - Real-time content generation and analysis
  - Copy to clipboard functionality
  - Import generated content for analysis

## Tech Stack

- **Backend**:
  - FastAPI (Python web framework)
  - SQLAlchemy (ORM)
  - PostgreSQL (Database)
  - Hugging Face API (AI models)

- **Frontend**:
  - HTML5
  - CSS3
  - JavaScript
  - Bootstrap 5
  - Font Awesome icons

## Prerequisites

- Python 3.8+
- PostgreSQL
- Hugging Face API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kartik-kt/ai-content-analyzer.git
cd ai-content-analyzer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv requests jinja2 python-multipart
```

4. Create a `.env` file in the root directory with the following content:
```
HUGGINGFACE_API_KEY=your_huggingface_api_key
DATABASE_URL="postgresql://username:password@localhost:5432/dbname"
```

5. Create a PostgreSQL database and update the DATABASE_URL in `.env`

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

1. **Generating Content**:
   - Navigate to the "Generate" section
   - Enter a topic
   - Click "Generate Content"
   - Wait for the AI to generate the article

2. **Analyzing Content**:
   - Navigate to the "Analyze" section
   - Either paste your content or import generated content
   - Click "Analyze"
   - View readability and sentiment analysis results

## Project Structure

```
ai-content-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic models
│   ├── crud.py          # Database operations
│   ├── utility.py       # AI functionality
│   └── database.py      # Database configuration
├── templates/
│   └── index2.html      # Frontend template
├── static/              # Static files
├── .env                 # Environment variables
└── README.md           # Project documentation
```

## API Endpoints

- `GET /`: Main application interface
- `POST /generate/`: Generate content for a given topic
- `POST /analyze/`: Analyze content for readability and sentiment

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for providing the AI models
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Bootstrap](https://getbootstrap.com/) for the UI components 
