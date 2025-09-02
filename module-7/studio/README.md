# LangGraph Studio - Brainstorming Agent

A powerful AI agent built with LangGraph for brainstorming, research, and PRD generation with multiple storage backends.

## Features

- 🤖 **AI Brainstorming Agent** - Powered by GPT-4o
- 🔍 **Deep Research** - Multi-strategy web research with content verification
- 📋 **PRD Generation** - Create Product Requirements Documents
- 💾 **Multiple Storage Options** - Markdown, SQLite, JSON, MongoDB
- 🌐 **Web Browsing** - Integrated web search capabilities
- 📝 **File Operations** - Read, edit, and manage files
- 🧠 **Memory Management** - Persistent conversation memory

## Setup

### 1. Environment Setup

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional (for MongoDB storage)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=prd_database
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run LangGraph Studio

```bash
langgraph dev
```

The agent will automatically load API keys from the `.env` file.

## Available Tools

### Research & Information
- `browse_web` - Quick web search using Tavily
- `deep_research` - Comprehensive research with multiple strategies

### File Operations
- `read_file` - Read file contents
- `edit_file` - Edit files with search/replace
- `apply_patch` - Apply patches to files

### Memory & Storage
- `save_to_memory` - Save information to conversation memory

### PRD Generation
- `generate_prd` - Generate PRD and save to Markdown (default)
- `generate_prd_sqlite` - Generate PRD and save to SQLite database
- `generate_prd_json` - Generate PRD and save to JSON file database
- `generate_prd_mongodb` - Generate PRD and save to MongoDB (if available)

## Usage Examples

### Basic Research
```
What are the latest features in React 18?
```

### Deep Research
```
deep_research: "Compare AWS Lambda vs Google Cloud Functions performance", depth: "medium"
```

### PRD Generation
```
generate_prd_sqlite: "User Authentication System", "Implement secure login with OAuth", "Support Google, GitHub, and email/password auth"
```

## Storage Options

The system supports multiple storage backends for PRDs:

- **Markdown** (default): Human-readable files in `prds/` directory
- **SQLite**: Relational database storage in `prds.db`
- **JSON**: Structured file-based storage in `prds_json/`
- **MongoDB**: NoSQL document storage (requires MongoDB installation)

## API Keys

API keys are automatically loaded from the `.env` file. No manual input required during runtime.

- **OpenAI API Key**: Required for LLM functionality
- **Tavily API Key**: Required for web search features
- **LangSmith API Key**: Optional, for tracing and monitoring

## Troubleshooting

### API Key Issues
- Ensure `.env` file exists and contains valid API keys
- Check that `python-dotenv` is installed: `pip install python-dotenv`

### Storage Issues
- SQLite: No additional setup required
- JSON: Creates `prds_json/` directory automatically
- MongoDB: Requires MongoDB server and `pymongo` package

### Port Conflicts
If port 2024 is busy, LangGraph Studio will use an available port automatically.
