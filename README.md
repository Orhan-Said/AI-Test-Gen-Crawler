# Test Generation Crawler

## Overview

This project is a sophisticated test generation system that combines web crawling capabilities with automated test creation. It consists of a Python backend for crawling and test generation, along with a Next.js frontend interface for user interaction.

## Architecture

The system is built with a modular architecture consisting of several key components:

### Backend Components

- **Crawler (crawler.py)**: Handles web crawling functionality to extract relevant information from target websites
- **Generator (generator.py)**: Creates test cases based on crawled data
- **Analyzer (analyzer.py)**: Analyzes crawled content and structures for test generation
- **QA Validator (qa_validator.py)**: Validates generated tests for quality assurance
- **Repository Integrator (repo_integrator.py)**: Manages integration with version control systems
- **API (api.py)**: Provides RESTful endpoints for frontend communication

### Frontend Components (UI/)

- Next.js application with TypeScript
- Tailwind CSS for styling
- Component-based architecture
- Theme support

### Database

- Supabase integration for data persistence
- Custom client implementation in utils/SupabaseClient.py

## Setup Instructions

### Prerequisites

- Python 3.x
- Node.js and npm
- Supabase account

### Backend Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure environment variables

### Frontend Setup

1. Navigate to the UI directory:
   ```bash
   cd UI
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

### Basic Usage

1. Start the backend server
2. Launch the frontend application
3. Use the web interface to:
   - Configure crawling parameters
   - Start crawling sessions
   - Generate tests
   - View and export results

### API Endpoints

The system exposes several RESTful endpoints:

- `POST /api/crawl`: Start a new crawling session
- `GET /api/status`: Check crawling status
- `POST /api/generate`: Generate tests from crawled data
- `GET /api/results`: Retrieve generated test results

## Configuration

### Environment Variables

Required environment variables (see `.env.example`):

- Database credentials
- API keys
- Service configurations

### Frontend Configuration

- `next.config.ts`: Next.js configuration
- `tailwind.config.ts`: Tailwind CSS settings
- `tsconfig.json`: TypeScript configuration

## Components

### Crawler

The crawler component supports:

- Configurable crawling depth
- URL filtering
- Rate limiting
- Custom header support

### Generator

Test generation features:

- Multiple test formats
- Customizable templates
- Validation rules
- Export options

### Analyzer

Analysis capabilities:

- Content structure analysis
- Pattern recognition
- Test coverage optimization

### QA Validator

Validation features:

- Syntax checking
- Coverage analysis
- Quality metrics
- Compliance verification

### Repository Integrator

Version control features:

- Git integration
- Commit management
- Branch handling
- CI/CD support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

[License details to be added]
