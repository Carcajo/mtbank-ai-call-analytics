# 🏦 MTBank — AI Call Analytics Pipeline

> Technical test assignment for the **AI Engineer (AI Agents & Contact Center Speech Analytics)** position at MTBank.

An end-to-end AI-powered speech analytics platform that automatically transcribes customer service calls, performs speaker diarization, orchestrates multiple LLM agents for business analysis, and delivers structured insights through both a REST API and OpenWebUI Pipelines.

---

## 📋 Table of Contents

* [Overview](#-overview)
* [Key Features](#-key-features)
* [Technology Stack Rationale](#-technology-stack-rationale)
* [Requirements](#-requirements)
* [Environment Variables](#-environment-variables)
* [Installation & Local Development](#-installation--local-development)
* [Docker Deployment](#-docker-deployment)

---

# 📖 Overview

Contact centers process thousands of customer interactions every day. Manual quality control and compliance verification are expensive, time-consuming, and difficult to scale.

This project provides a prototype AI-powered analytics platform capable of:

* Automatically transcribing customer calls using local ASR models
* Performing speaker diarization (Operator / Client)
* Classifying customer requests
* Evaluating service quality
* Detecting compliance violations
* Generating concise business summaries
* Producing actionable recommendations
* Integrating directly into OpenWebUI chat workflows

The entire pipeline is containerized and can be launched with a single Docker Compose command.

---

# ✨ Key Features

### 🎙 Local Speech Recognition

* Faster-Whisper based ASR
* Russian language optimized
* Offline processing
* Timestamped transcription
* Multi-format audio support

### 👥 Speaker Diarization

* PyAnnote-based speaker separation
* Operator / Client role assignment
* Timestamp preservation
* Structured dialogue output

### 🤖 Multi-Agent Analytics

Four specialized AI agents:

| Agent                | Responsibility                          |
| -------------------- | --------------------------------------- |
| 🏷️ Classifier       | Topic detection and priority assessment |
| ⭐ Quality Agent      | Operator quality checklist evaluation   |
| 🛡️ Compliance Agent | Compliance and security validation      |
| 📝 Summarizer        | Executive summary and action items      |

### 🔄 LangGraph Orchestration

* Deterministic execution flow
* Shared immutable state
* Predictable outputs
* Easy extensibility

### 🌐 REST API

* FastAPI backend
* Multipart audio upload
* JSON responses
* Swagger documentation

### 💬 OpenWebUI Integration

* Native OpenWebUI Pipeline
* Chat-based interaction
* Real-time progress updates
* Markdown report rendering

### 🧪 Testing

* Unit tests for every agent
* End-to-end integration testing
* Pydantic schema validation

### 📊 Evaluation

* WER (Word Error Rate) benchmarking
* Multiple audio formats
* Telephone-quality audio testing

---

---

## LangGraph Workflow

```text
START
  |
  v
Classifier
  |
  v
Quality
  |
  v
Compliance
  |
  v
Summarizer
  |
  v
END
```

The workflow follows a strict sequential execution model.

Each agent receives the current immutable state and appends only its own output.

This approach ensures:

* deterministic execution;
* reduced LLM overhead;
* easier debugging;
* predictable production behavior.

---

# 🧠 Technology Stack Rationale

## Agent Orchestration

### LangGraph (StateGraph)

The project uses LangGraph with a sequential graph:

```text
Classifier
    ↓
Quality
    ↓
Compliance
    ↓
Summarizer
```

### Why LangGraph?

Advantages:

* Explicit state management
* Deterministic execution
* Minimal orchestration overhead
* Easy debugging
* Production readiness

### Why Not a Supervisor Pattern?

A Supervisor architecture is useful when:

* dynamic routing is required;
* agents need iterative refinement;
* tasks can be delegated recursively.

None of these conditions are necessary for this assignment.

Every analytical step depends on the same transcript and executes exactly once.

Therefore, a sequential StateGraph provides a simpler and more robust solution.

---

## ASR Engine

### faster-whisper

Selected because of:

* excellent Russian language quality;
* lower memory consumption;
* significantly faster inference compared to original Whisper;
* active community support.

Model used:

```text
medium
```

The implementation can be upgraded to larger models if additional accuracy is required.

---

## Speaker Diarization

### pyannote.audio

Chosen because it provides:

* state-of-the-art speaker segmentation;
* reliable diarization quality;
* seamless integration with Hugging Face models.

The diarization output is mapped into:

```text
Operator
Client
```

roles used by downstream analytics agents.

---

## Large Language Model

### Qwen 2.5 7B Instruct

Accessed through OpenRouter.

Reasons for selection:

* strong Russian language understanding;
* reliable instruction following;
* good cost-to-quality ratio;
* structured JSON output support;
* no VPN requirements.

---

## Backend Framework

### FastAPI

Selected because it offers:

* high performance;
* automatic OpenAPI generation;
* async support;
* excellent developer experience.

---

## Containerization

### Docker + Docker Compose

The entire stack can be launched using a single command:

```bash
docker compose up -d --build
```

Benefits:

* reproducibility;
* portability;
* simplified deployment;
* environment consistency.

---

# ⚙️ Requirements

The project was developed and tested with:

```text
Python 3.10+
Docker 24+
Docker Compose
```

Required accounts:

* Hugging Face
* OpenRouter

---

# 🔐 Environment Variables

Create a local `.env` file based on `.env.example`.

Example:

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxx

OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx

API_URL=http://ai-backend:8000/analyze
```

### Variables

| Variable           | Description                                   |
| ------------------ | --------------------------------------------- |
| HF_TOKEN           | Hugging Face access token for pyannote models |
| OPENROUTER_API_KEY | OpenRouter API key                            |
| API_URL            | Internal API endpoint                         |

---

# 🚀 Installation & Local Development

## Clone Repository

```bash
git clone https://github.com/Carcajo/mtbank-ai-call-analytics.git

cd your-repository
```

---

## Create Environment File

```bash
cp .env.example .env
```

Fill the environment variables.

---

## Build Containers

```bash
docker compose build
```

---

## Start Services

```bash
docker compose up -d
```

---

## Verify Startup

Check logs:

```bash
docker logs -f mtbank-ai-backend
```

The first startup may take several minutes because Whisper and PyAnnote models must be downloaded and initialized.

---

# 🐳 Docker Deployment

The entire application stack is fully containerized.

Launch everything with:

```bash
docker compose up -d --build
```

Services started:

| Service            | Purpose            |
| ------------------ | ------------------ |
| FastAPI Backend    | REST API           |
| ASR Pipeline       | Speech Recognition |
| LangGraph Agents   | Analytics          |
| OpenWebUI Pipeline | Chat Integration   |

Once started successfully:

```text
http://localhost:8000/docs
```

provides interactive Swagger documentation.

---

# 📊 Analytics Components

The system exposes a single REST endpoint that accepts an audio recording, performs speech recognition, orchestrates AI agents, and returns a structured JSON response.

---

# 🔄 Processing Pipeline

The complete workflow is shown below:

```text
Audio File
    │
    ▼
Speech Recognition (faster-whisper)
    │
    ▼
Speaker Diarization (pyannote.audio)
    │
    ▼
Structured Transcript
    │
    ▼
LangGraph Orchestration
    │
    ├── Classifier
    ├── Quality
    ├── Compliance
    └── Summarizer
    │
    ▼
Structured JSON
    │
    ▼
Markdown Report (OpenWebUI)
```

---

# 🌐 REST API

## Analyze Call

```http
POST /analyze
```

### Content-Type

```text
multipart/form-data
```

### Request

| Field | Type       | Description          |
| ----- | ---------- | -------------------- |
| file  | Audio File | WAV, MP3, OGG or M4A |

Example:

```bash
curl -X POST \
  -F "file=@test_data/call_dialog.m4a" \
  http://localhost:8000/analyze
```

---

# 📄 Example JSON Response

```json
{
  "transcript": [
    {
      "speaker": "Operator",
      "start": 0.0,
      "end": 5.52,
      "text": "Good afternoon. MTBank Contact Center."
    }
  ],
  "classification": {
    "topic": "Cards",
    "priority": "medium"
  },
  "quality_score": {
    "total": 100,
    "checklist": {
      "greeting": true,
      "need_detection": true,
      "solution_provided": true,
      "farewell": true
    }
  },
  "compliance": {
    "passed": true,
    "issues": []
  },
  "summary": "Customer requested information about SMS service fees.",
  "action_items": []
}
```

---

# 🤖 AI Agents

## 🏷️ Classifier

Responsibilities:

* Detect call topic
* Estimate priority
* Produce structured JSON

Output:

```json
{
  "topic": "Cards",
  "priority": "medium"
}
```

---

## ⭐ Quality Agent

Evaluates operator performance.

Checklist:

* Greeting
* Need detection
* Solution provided
* Farewell

Returns:

* checklist
* total score

---

## 🛡️ Compliance Agent

Detects:

* prohibited phrases
* missing disclaimers
* policy violations
* suspicious recommendations

Output example:

```json
{
  "passed": true,
  "issues": []
}
```

---

## 📝 Summarizer

Produces:

* concise summary
* action items

Example:

```text
Customer requested information regarding SMS notifications.
The operator explained the service fee and successfully disabled the feature.
```

---

# 📝 Structured JSON Logging

Financial applications require traceable execution.

Each agent is wrapped by a logging decorator.

Logged events include:

* start
* finish
* execution time
* input state
* output state
* exceptions

Example:

```json
{
  "timestamp":"2026-07-09 11:20:02",
  "level":"INFO",
  "event":"agent_start",
  "agent":"Classifier"
}
```

Successful execution:

```json
{
  "timestamp":"2026-07-09 11:20:04",
  "event":"agent_success",
  "duration_sec":1.42
}
```

Benefits:

* production monitoring
* debugging
* audit trail
* observability

---

# 🧪 Testing

The project contains automated tests for every critical component.

## Unit Tests

Each AI agent is tested independently.

Covered functionality:

* output schema
* Pydantic validation
* prompt execution
* response formatting

Run:

```bash
pytest tests/
```

---

## Integration Test

The entire LangGraph pipeline is tested end-to-end.

Pipeline verification includes:

* transcription
* orchestration
* state propagation
* JSON generation

Example:

```text
5 passed in 7.56s
```

---

# 📉 ASR Evaluation

Speech recognition quality was evaluated using the **Word Error Rate (WER)** metric.

Normalization:

* lowercase conversion
* punctuation removal
* whitespace normalization

Evaluation library:

```text
jiwer
```

---

## Results

| Audio                | WER   | Status | Description            |
| -------------------- | ----- | ------ | ---------------------- |
| atm_complaint.mp3    | 0.00% | ✅      | Client monologue       |
| call_dialog.m4a      | 0.00% | ✅      | Multi-speaker dialogue |
| transfer_issue.mp3   | 0.00% | ✅      | Money transfer issue   |
| credit_info.mp3      | 2.94% | ✅      | Credit consultation    |
| call_dialog_8khz.wav | 2.89% | ✅      | Telephone quality      |

Average dataset WER:

```text
1.17%
```

Recalculate:

```bash
python evaluate_wer.py
```

---

# 💬 OpenWebUI Integration

The repository includes a native OpenWebUI Pipeline.

Workflow:

1. User uploads an audio file.
2. Pipeline receives the request.
3. Speech recognition starts.
4. LangGraph executes all agents.
5. Markdown report is generated.
6. Response is streamed back into chat.

Streaming messages:

```text
⏳ Loading audio...

🎙 Running speech recognition...

🤖 Launching AI agents...

📊 Preparing report...
```

The final report contains:

* transcript
* classification
* quality assessment
* compliance report
* executive summary
* action items

---

# 📦 Supported Audio Formats

The pipeline supports:

* WAV
* MP3
* OGG
* M4A

Additional formats can be added through FFmpeg.

---

# 🌐 Demo

After deployment the following services become available:

| Service    | URL                           |
| ---------- | ----------------------------- |
| Swagger UI | http://localhost:8000/docs    |
| REST API   | http://localhost:8000/analyze |
| OpenWebUI  | Configurable                  |

---

# 🚀 Future Improvements

Potential enhancements:

* WebSocket real-time transcription
* Grafana dashboards
* Trend analysis agent
* RAG knowledge base
* Kubernetes deployment
* Horizontal scaling
* Redis task queue
* Parallel agent execution
* Automatic language detection
* Sentiment analysis

---

# 📚 References

Main technologies used in this project:

* FastAPI
* LangGraph
* LangChain
* faster-whisper
* pyannote.audio
* OpenRouter
* Qwen 2.5 Instruct
* Docker
* Pytest
* Pydantic
* jiwer

---

# 📄 License

This repository was developed exclusively as a technical assessment for the **MTBank AI Engineer** position.

It is intended for demonstration and educational purposes only.

---

# 👨‍💻 Author

Developed as part of the MTBank AI Engineer technical assignment.

---

# ✅ Assignment Checklist

| Requirement                  | Status |
| ---------------------------- | ------ |
| OpenWebUI Pipeline           | ✅      |
| Faster-Whisper ASR           | ✅      |
| Speaker Diarization          | ✅      |
| LangGraph Multi-Agent System | ✅      |
| FastAPI REST API             | ✅      |
| Docker Compose               | ✅      |
| JSON Logging                 | ✅      |
| Unit Tests                   | ✅      |
| Integration Tests            | ✅      |
| `.env.example`               | ✅      |
| WER Evaluation               | ✅      |
| Project Documentation        | ✅      |
| OpenWebUI Integration        | ✅      |
| Structured JSON Response     | ✅      |

---

## 🎯 Project Summary

This project demonstrates a complete AI-powered speech analytics pipeline for contact center conversations.

The solution combines local automatic speech recognition, speaker diarization, deterministic multi-agent orchestration with LangGraph, RESTful APIs, Docker-based deployment, and OpenWebUI integration into a production-style architecture suitable for enterprise AI applications.