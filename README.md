# FastAPI Audio Meeting Report Generator

A production-ready **FastAPI-based report generation application** with authentication, asynchronous operations, and Docker support.

The application allows **authenticated users** to upload audio files (e.g., meeting recordings) and automatically generate a **PDF meeting report**.


## Generated Report Includes:
- Title  
- Summary  
- Topics Discussed  
- Decisions Made  
- Action Items  
- Transcript  


## Supported Audio & Limits
- Supported audio formats: **`.mp3`, `.wav`, `.m4a`**
- Maximum audio file size: **100 MB**



## Models & APIs

### Transcription
- Uses AssemblyAI’s **Universal** speech model (default model)

### Summary & Notes Generation
- Uses **`mistral-medium-latest`** via the Chat Completion API  
- Other models such as Mistral Small and Mistral Large were tested, but Medium performs best for this task  
- Feel free to experiment with different Mistral models



## Architecture Notes & Limitations
- Currently supports **fixed transcription and chat-completion models** via external APIs  
- Future versions may:
  - Support **local LLMs**
  - Introduce a **generic provider interface** for multiple transcription and LLM services

### Storage
- Audio files and generated reports are currently stored using **local storage**
- This is not recommended for production use
- Future versions will migrate storage to **S3 buckets** or equivalent cloud storage

### Intermediate Results
- Transcriptions are not currently stored
- Persisting intermediate results could enable:
  - Downloading reports in multiple formats
  - Regenerating summaries using different models


## Features

- **Modern Python**: Type hints, async/await syntax, and the latest FastAPI features
- **JWT Authentication**: Complete authentication system with access and refresh tokens
- **SQLAlchemy with Async**: Fully async database operations using SQLAlchemy 2.0+
- **Alembic Migrations**: Database schema migrations with Alembic
- **Role-based Access Control**: User roles with different permission levels (active, staff, superuser)
- **Docker Support**: Ready-to-use Docker and Docker Compose configurations
- **Developer-friendly**: Auto-reload, debugging, and development tools
- **Production-ready**: Configuration for deployment in production environments

## Project Structure

```
.
├── alembic/                 # Database migrations
├── app/                     # Main application package
│   ├── api/                 # API endpoints
│   ├── core/                # Core functionality (config, security)
│   ├── db/                  # Database session and base
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
|   |__ repositories         # CURD operations
├── docker-compose.yml       # Docker Compose for production
├── docker-compose.dev.yml   # Docker Compose for development
├── Dockerfile               # Docker configuration
├── alambic.ini              # Alembic configuration
├── main.py                  # Application entry point
├── pyproject.toml           # Project dependencies and metadata
├── start.sh                 # Production startup script
└── start-dev.sh             # Development startup script
```

## Requirements

- Python 3.11+
- Docker (optional)
- To run this project, you will need **two API keys**:
  - **AssemblyAI API key**
    - Universal model includes **$50 free credit**
  - **Mistral API key**
    - Includes limited free access

## Installation

### Using Docker (recommended)

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd report-generator-rakamai
   ```

2. Start the application with Docker Compose:
   ```bash
   # For development
   docker-compose -f docker-compose.dev.yml up --build

   # For production
   docker-compose up --build
   ```

3. The API will be available at http://localhost:8000

### Local Development

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd report-generator-rakamai
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up environment variables (create a `.env` file):
   ```
   DEBUG=true
   SECRET_KEY=your-secret-key
   DB_ENGINE=sqlite  # or postgresql
   # For PostgreSQL, add these:
   # DB_USER=postgres
   # DB_PASSWORD=password
   # DB_HOST=localhost
   # DB_PORT=5432
   # DB_NAME=app
   # AUDIO_UPLOAD_DIR = audio
   # MAX_UPLOAD_SIZE = 100000000
   # ASSEMBLYAI_BASE_URL = "https://api.assemblyai.com/v2"
   # ASSEMBLYAI_API_KEY = your-api-key
   # DEFAULT_ASSEMBLYAI_MODEL = universal
   # MISTRAL_API_KEY = your-api-key
   # MISTRAL_BASE_URL = https://api.mistral.ai/v1
   # DEFAULT_MISTRAL_MODEL = mistral-medium-latest
   # REPORT_UPLOAD_DIR = reports
   # VERSION = 1.2.0 # current version of app
   ```

5. Run migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the application:
   ```bash
   uvicorn main:app --reload
   ```

7. The API will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Authenticate and get tokens
- `POST /auth/token/refresh` - Refresh access token
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user information

### System

- `GET /health` - Health check endpoint

### Audio

- `POST /audio/upload` - Upload audio file (returns `audio_id`)

### Report
- `POST /report/generate` - Create background job for a report from `audio_id` (returns `job_id`)
- `GET /report/status/{job_id}` - Query processing status for a job
- `GET /report/download/{job_id}` - Download generated PDF when job is `summarized`


## Configuration

The application is configured through environment variables which can be set in a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `true` |
| `SECRET_KEY` | JWT secret key | `supersecretkey` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration time | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration time | `7` |
| `CORS_ORIGINS` | CORS allowed origins | `["*"]` |
| `DB_ENGINE` | Database engine | `sqlite` |
| `DB_USER` | Database user | `""` |
| `DB_PASSWORD` | Database password | `""` |
| `DB_HOST` | Database host | `""` |
| `DB_PORT` | Database port | `""` |
| `DB_NAME` | Database name | `app.db` |
| `AUDIO_UPLOAD_DIR` | Location of audio files | `audio` |
| `REPORT_UPLOAD_DIR` | Location of reports | `reports` |
| `MAX_UPLOAD_SIZE` | Max size of audio file | `100000000` |
| `ASSEMBLYAI_BASE_URL` | URL | `https://api.assemblyai.com/v2` |
| `ASSEMBLYAI_API_KEY` | API key| `""` |
| `DEFAULT_ASSEMBLYAI_MODEL` | Speech model | `universal` |
| `MISTRAL_BASE_URL` | URL | `https://api.mistral.ai/v1` |
| `MISTRAL_API_KEY` | API key | `""` |
| `DEFAULT_MISTRAL_MODEL` | Mistral model | `"mistral-medium-latest"` |
| `VERSION` |  App version | `""` |

## Development

### Running Tests

```bash
pytest
```

### Code Quality Tools

The project uses several tools to ensure code quality:

- **Black**: Code formatter
- **isort**: Import sorter
- **mypy**: Static type checking
- **pre-commit**: Git hooks for code quality checks

To set up pre-commit hooks:

```bash
pre-commit install
```

## Database

The template supports SQLite for development and PostgreSQL for production. The default is SQLite.

### Migrations

To create a new migration after changing models:

```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

## Docker

The project includes Docker configurations for both development and production:

- `docker-compose.yml`: Production setup
- `docker-compose.dev.yml`: Development setup with hot-reload

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b ft/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin ft/my-feature`


## Authors

This project was developed using a FastAPI template provided by **Rakam AI** (https://www.rakam.ai/).

The template includes authentication, user login APIs, and the initial project setup.

- **Clemmie Melegi** (Rakam AI) — Provided the FastAPI template, authentication system, and initial application setup  
- **Nageeta Kumari** — Completed the take-home assignment, worked on **Audio** and **Report** APIs including business logic for transcribing and report generation.
