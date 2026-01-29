# BI Dashboard Agent - AI-Powered Business Intelligence Platform

A free, open-source BI dashboard platform with AI-powered natural language interface for creating visualizations, analyzing data, and generating insights.

**Practical Agent System** - Performs real actions (creates dashboards, transforms data, exports files) with comprehensive evaluation metrics.

## 📚 Project Documentation

- **[System Architecture](SYSTEM_ARCHITECTURE.md)** - Complete architecture diagrams and component interactions
- **[Agent Description](AGENT_DESCRIPTION.md)** - Detailed description of agent capabilities, tools, and reasoning style
- **[Project Requirements Checklist](PROJECT_REQUIREMENTS_CHECKLIST.md)** - Verification of all requirements
- **[Demo Video Script](DEMO_VIDEO_SCRIPT.md)** - Script for creating the demo video

## 🚀 Features

- **AI-Powered Dashboard Creation** - Create dashboards using natural language commands
- **Q&A Chatbot** - Ask questions about your data and get intelligent answers powered by Gemini
- **Multiple LLM Support** - Gemini, Ollama, or HuggingFace
- **Data Transformation** - Filter, aggregate, and transform data with AI assistance
- **Power BI Export** - Export dashboards to Power BI format
- **Real-time Evaluation** - Comprehensive agent performance metrics
- **Local-First Architecture** - Privacy-focused, no vendor lock-in

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Gemini API Key** (recommended) or Ollama installed

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Project
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies

```bash
npm install
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend (optional)
VITE_API_BASE_URL=http://localhost:8000
```

**Get Gemini API Key:**
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and add to `.env` file

## 🏃 Running the Application

### Start Backend

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Or use the development script:

```bash
python scripts/run_dev.py
```

### Start Frontend

```bash
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage

### 1. Upload Data

- Click "Upload Dataset" button
- Select CSV or Excel file
- Data is automatically analyzed and schema detected

### 2. Create Dashboards with AI

Use natural language commands in the AI Console:

**Visualization Commands:**
- "Create a bar chart showing sales by region"
- "Show me KPIs for total revenue and orders"
- "Generate a complete dashboard"
- "Add a line chart for revenue over time"

**Question Commands:**
- "What are the top 5 products by sales?"
- "What's the average revenue per region?"
- "Which region has the highest sales?"
- "How many records are in the dataset?"

**Analysis Commands:**
- "Explain this chart"
- "What insights can I get from this data?"
- "What does the revenue trend tell us?"

### 3. Customize Dashboards

- Click on widgets to inspect and modify
- Use the AI console to make changes
- Export to Power BI or CSV

## 🏗️ Architecture

```
Frontend (React + TypeScript + Vite)
    ↓ HTTP/REST API
Backend (FastAPI)
    ├── Data Ingestion (CSV/Excel)
    ├── Transformation Engine
    ├── Dashboard Generator
    ├── AI Agent Service
    │   ├── Intent Parser (LLM)
    │   ├── Action Generator
    │   └── Evaluation System
    └── Storage (SQLite + File System)
```

### Key Components

- **Frontend**: React dashboard with AI console, widget system, and evaluation dashboard
- **Backend**: FastAPI REST API with data processing and AI agent
- **AI Agent**: Natural language processing with Gemini/Ollama/HuggingFace
- **Evaluation System**: Comprehensive metrics tracking (6 metrics)

## 📊 Agent Evaluation System

The platform includes a built-in evaluation system with **6 benchmarking metrics**:

1. **Task Success Rate** - Percentage of successfully completed tasks
2. **Action Execution Correctness** - How well actions match user intents
3. **Latency** - Response time measurements
4. **Cost Efficiency** - API call cost tracking (Gemini pricing)
5. **Reasoning Length** - Token usage (prompt + response)
6. **Tool Usage Correctness** - Verification of correct tools/actions used

### View Evaluation Metrics

**Via API:**
```bash
GET /api/v1/evaluation/summary
GET /api/v1/evaluation/results
GET /api/v1/evaluation/metrics/{metric_name}
```

**Via Frontend:**
Add route to `App.tsx`:
```tsx
import { EvaluationDashboard } from './components/dashboard/EvaluationDashboard';
<Route path="/evaluation" element={<EvaluationDashboard />} />
```

## 🔌 API Endpoints

### Data Management
- `POST /api/v1/upload` - Upload dataset
- `GET /api/v1/datasets` - List datasets
- `GET /api/v1/datasets/{id}` - Get dataset details

### Dashboard
- `GET /api/v1/dashboard/{id}` - Get dashboard
- `POST /api/v1/dashboard` - Create dashboard
- `PUT /api/v1/dashboard/{id}` - Update dashboard

### AI Agent
- `POST /api/v1/ai/process` - Process AI command
- `GET /api/v1/ai/history` - Get conversation history

### Export
- `POST /api/v1/export/powerbi` - Export to Power BI (.pbix)
- `POST /api/v1/export/powerbi/json` - Export Power BI JSON
- `POST /api/v1/export/csv` - Export to CSV

### Evaluation
- `GET /api/v1/evaluation/summary` - Get evaluation summary
- `GET /api/v1/evaluation/results` - Get evaluation results
- `GET /api/v1/evaluation/metrics/{metric}` - Get specific metric
- `POST /api/v1/evaluation/export` - Export evaluation data

## 🎨 Supported Visualizations

- **Bar Charts** - Category comparisons
- **Line Charts** - Time series and trends
- **Pie Charts** - Distribution analysis
- **KPI Cards** - Key metrics display
- **Tables** - Raw data views

## 📤 Export Options

### Power BI Export

1. **Export .pbix file:**
   - Click Download button in toolbar
   - Opens in Power BI Desktop
   - May require manual data connection setup

2. **Export JSON + CSV (Recommended):**
   - Export JSON definition
   - Export CSV data
   - Import CSV into Power BI Desktop
   - Recreate visuals using JSON as reference

### CSV Export

- Export complete dataset as CSV
- Includes all transformations
- Compatible with Excel and other tools

## 🔧 Configuration

### LLM Provider Options

**Gemini (Recommended):**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
```

**Ollama (Local):**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**HuggingFace (Local):**
```env
LLM_PROVIDER=huggingface
HF_MODEL_NAME=google/flan-t5-base
```

### Database

Default: SQLite (`./database/bi_dashboard.db`)

To use PostgreSQL/MySQL, update `database_url` in `.env`:
```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## 📁 Project Structure

```
Project/
├── ai_agent/              # AI agent logic
│   ├── agent.py          # Main agent orchestrator
│   ├── intent_parser.py  # Natural language parsing
│   ├── action_generator.py # Action generation
│   └── llm/              # LLM clients (Gemini, Ollama, HuggingFace)
├── backend/               # FastAPI backend
│   ├── api/routes/       # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Database models
│   └── main.py           # Application entry point
├── src/                   # React frontend
│   ├── components/       # React components
│   ├── contexts/         # React contexts
│   └── utils/            # Utility functions
├── data/                  # Data storage
│   ├── uploads/          # Uploaded datasets
│   └── cache/            # Cached data
└── database/              # SQLite database
```

## 🐛 Troubleshooting

### Backend Not Starting

- Check Python version: `python --version` (need 3.11+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is available

### Frontend Not Starting

- Check Node.js version: `node --version` (need 18+)
- Install dependencies: `npm install`
- Check port 5173 is available

### AI Agent Not Working

- **Gemini**: Verify API key in `.env` file
- **Ollama**: Ensure Ollama service is running
- Check backend logs for error messages

### Data Upload Issues

- Verify file format (CSV or Excel)
- Check file size (max 10MB default)
- Ensure proper column headers

## 🚀 Future Enhancements

Easy to add features (see implementation guide):
- More visualization types (scatter, heatmap, area charts)
- PDF/PNG export
- Dashboard templates
- Shareable dashboard links
- Scheduled reports
- Real-time data connections
- Multi-user support

## 📝 Development

### Backend Development

```bash
# Run with auto-reload
python -m uvicorn backend.main:app --reload

# Run tests
pytest
```

### Frontend Development

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📄 License

This project is open-source and free to use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Gemini API**: https://ai.google.dev/
- **Ollama**: https://ollama.ai/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/

## 💡 Tips

- Use clear, specific commands for best results
- Example prompts are available in the AI console
- Evaluation metrics help optimize agent performance
- Export to Power BI for advanced analysis
- Q&A chatbot provides data insights without creating charts

## 📚 Project Documentation

For detailed information about the agent system:

- **[System Architecture](SYSTEM_ARCHITECTURE.md)** - Complete architecture diagrams and component interactions
- **[Agent Description](AGENT_DESCRIPTION.md)** - Detailed description of agent capabilities, tools, and reasoning style
- **[Project Requirements Checklist](PROJECT_REQUIREMENTS_CHECKLIST.md)** - Verification of all requirements
- **[Demo Video Script](DEMO_VIDEO_SCRIPT.md)** - Script for creating the demo video
- **[Submission Checklist](SUBMISSION_CHECKLIST.md)** - Final submission guide

---

**Built with ❤️ using FastAPI, React, TypeScript, and Gemini AI**

**Practical Agent System** - Performs real actions with comprehensive evaluation metrics
