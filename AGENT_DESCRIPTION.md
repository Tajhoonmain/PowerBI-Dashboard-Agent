# Agent Description - BI Dashboard Agent

## Overview

The **BI Dashboard Agent** is a practical AI agent system that performs real actions to create, modify, and analyze business intelligence dashboards through natural language commands. Unlike text-only agents, this system executes actual dashboard modifications, data transformations, and generates visualizations.

## Tasks Performed

### 1. Dashboard Creation
- **Action**: Creates complete dashboards with multiple widgets
- **Example**: "Generate a complete dashboard" → Creates KPIs, charts, and tables
- **Real Output**: Actual React components rendered in the UI

### 2. Visualization Generation
- **Action**: Adds individual charts (bar, line, pie, KPI cards, tables)
- **Example**: "Create a bar chart showing sales by region"
- **Real Output**: Functional chart widget with data visualization

### 3. Data Analysis & Q&A
- **Action**: Answers questions about data using pandas analysis + LLM
- **Example**: "What are the top 5 products by sales?"
- **Real Output**: Data-driven answer with specific numbers and insights

### 4. Chart Explanations
- **Action**: Explains existing charts with insights
- **Example**: "What does this chart mean?"
- **Real Output**: Detailed analysis with business implications

### 5. Dashboard Modifications
- **Action**: Modifies existing widgets (change type, axes, filters)
- **Example**: "Change the bar chart to a line chart"
- **Real Output**: Widget updated in real-time

### 6. Data Transformations
- **Action**: Applies data transformations (filter, aggregate, rename)
- **Example**: "Filter data where sales > 1000"
- **Real Output**: Transformed dataset applied to dashboard

### 7. Export Operations
- **Action**: Exports dashboards to Power BI or CSV
- **Example**: "Export to Power BI"
- **Real Output**: Downloadable .pbix or CSV file

## Tools Used

### Custom Tools (Action System)

1. **Dashboard Generator Tool**
   - **Purpose**: Creates dashboard widgets from data
   - **Input**: Dataset, column metadata, widget specifications
   - **Output**: Widget configurations (JSON)
   - **Action**: Generates actual React components

2. **Data Transformation Tool**
   - **Purpose**: Applies data transformations
   - **Input**: Dataset, transformation steps
   - **Output**: Transformed data
   - **Action**: Modifies actual data in memory

3. **Chart Creator Tool**
   - **Purpose**: Creates specific chart types
   - **Input**: Chart type, axes, data
   - **Output**: Chart widget configuration
   - **Action**: Adds widget to dashboard

4. **Data Analyzer Tool** (for Q&A)
   - **Purpose**: Analyzes data to answer questions
   - **Input**: Question, dataset
   - **Output**: Analysis results + LLM-generated answer
   - **Action**: Performs pandas operations + generates insights

5. **Power BI Exporter Tool**
   - **Purpose**: Exports dashboard to Power BI format
   - **Input**: Dashboard configuration, data
   - **Output**: .pbix file
   - **Action**: Creates downloadable file

6. **Evaluation Tracker Tool**
   - **Purpose**: Tracks agent performance metrics
   - **Input**: Intent, action, result
   - **Output**: Evaluation metrics
   - **Action**: Stores metrics in database

### LLM Integration

- **Gemini API** (Primary): Function calling via structured JSON output
- **Ollama** (Fallback): Local LLM for privacy
- **HuggingFace** (Alternative): Free local option

### External APIs

- **Google Gemini API**: For intent parsing and Q&A
- **Power BI REST API** (Optional): For direct Power BI integration

## Reasoning Style

### ReAct Pattern (Reasoning + Acting)

The agent follows a **ReAct-like** pattern:

1. **Reason**: 
   - Parse user command with LLM (Intent Parser)
   - Understand context (dashboard state, available columns)
   - Determine action type and parameters

2. **Act**:
   - Generate concrete action (Action Generator)
   - Execute tool (Dashboard Generator, Transformer, etc.)
   - Modify dashboard state

3. **Observe**:
   - Check action success
   - Evaluate correctness
   - Track metrics

4. **Reflect**:
   - Store in conversation history
   - Update evaluation metrics
   - Learn from results

### Planner-Executor Elements

- **Planner (Intent Parser)**: Determines what action to take
- **Executor (Action Generator)**: Performs the action
- **Evaluator**: Assesses performance and correctness

### RAG-like Context Passing

- Dataset data passed to LLM for Q&A
- Column metadata for intent understanding
- Dashboard state for context-aware actions
- Conversation history for continuity

## Technologies Used

### Core Framework
- **FastAPI**: REST API backend
- **React + TypeScript**: Frontend framework
- **SQLAlchemy**: Database ORM

### LLM Integration
- **Google Gemini API**: Primary LLM (structured JSON output)
- **Custom LLM Clients**: Gemini, Ollama, HuggingFace wrappers
- **Function Calling**: Via structured JSON (not OpenAI functions, but similar pattern)

### Data Processing
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical operations
- **OpenPyXL**: Excel file handling

### Visualization
- **Recharts**: React charting library
- **Plotly**: Backend chart generation (optional)

### Evaluation
- **Custom Evaluation System**: Similar to Graphene/AgentEval
- **SQLite**: Metrics storage
- **Real-time Tracking**: Automatic metric calculation

## Agent Capabilities

### ✅ Performs Real Actions (Not Just Text)

1. **Creates Actual Widgets**: React components rendered in UI
2. **Modifies Dashboard State**: Real-time updates
3. **Executes Data Transformations**: Actual data processing
4. **Generates Files**: Power BI exports, CSV downloads
5. **Analyzes Data**: Pandas operations with real results

### ✅ Tool Integration

- **Custom Tool System**: 6+ specialized tools
- **LLM Function Calling**: Structured JSON output (similar to OpenAI functions)
- **API Integration**: REST endpoints for all operations
- **Database Operations**: SQLAlchemy for persistence

### ✅ Memory & Context

- **Conversation History**: Tracks all interactions
- **Dashboard State**: Maintains current configuration
- **Dataset Context**: Passes data for analysis
- **Evaluation History**: Stores all metrics

### ✅ RAG-like Features

- **Context Retrieval**: Dataset data for Q&A
- **Metadata Passing**: Column info for intent parsing
- **State Awareness**: Dashboard context for actions

## Comparison to Standard Patterns

### vs. OpenAI Function Calling
- **Similar**: Structured JSON output, tool selection
- **Different**: Custom tool system, not OpenAI API

### vs. LangChain Tools
- **Similar**: Tool abstraction, agent orchestration
- **Different**: Custom implementation, no LangChain dependency

### vs. ReAct Framework
- **Similar**: Reasoning + Acting pattern
- **Different**: Specialized for BI dashboards

## Novel Aspects

1. **BI-Specific Agent**: Specialized for dashboard creation
2. **Real-Time Visualization**: Creates actual charts, not descriptions
3. **Q&A with Data Analysis**: Combines pandas + LLM for insights
4. **Comprehensive Evaluation**: 6 metrics with UI dashboard
5. **Power BI Integration**: Exports to enterprise BI tool

## Agent Workflow Example

```
User: "Create a bar chart showing sales by region"

1. Intent Parser (Gemini):
   - Input: Command + dashboard state + columns
   - Output: {"action_type": "add_chart", "parameters": {...}}

2. Action Generator:
   - Validates intent
   - Generates widget configuration
   - Creates chart component spec

3. Tool Execution:
   - Dashboard Generator creates bar chart widget
   - Data is aggregated by region
   - Widget added to dashboard

4. Evaluation:
   - Tracks success, latency, correctness
   - Stores metrics

5. Response:
   - Widget rendered in UI
   - User sees actual bar chart
```

## Technical Implementation

### Intent Parsing
- **LLM**: Gemini (structured JSON output)
- **Context**: Dashboard state, column metadata
- **Output**: Structured intent with action type and parameters

### Action Generation
- **Input**: Parsed intent
- **Process**: Validates, generates widget configs
- **Output**: Executable action with components

### Tool Execution
- **Tools**: Dashboard generator, transformer, exporter
- **Execution**: Real operations (not simulated)
- **Results**: Actual dashboard modifications

### Evaluation
- **Automatic**: Every action is tracked
- **Metrics**: 6 comprehensive metrics
- **Storage**: Database persistence
- **Visualization**: UI dashboard

## Compliance with Requirements

✅ **Performs Real Actions**: Creates actual dashboards
✅ **Tool Integration**: Custom tool system with 6+ tools
✅ **LLM Integration**: Gemini API (similar to function calling)
✅ **Evaluation**: 6 metrics (exceeds 5 requirement)
✅ **Documentation**: Complete system documentation

