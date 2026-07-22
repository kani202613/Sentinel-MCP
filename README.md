# SentinelMCP: Runtime Behavioral Security and Policy Enforcement Framework for MCP Agent Systems

> **"CrowdStrike for AI Agents"** — SentinelMCP is a runtime behavioral verification framework that continuously monitors whether an MCP agent's tool execution remains aligned with the user's intent using an empirically learned, decomposable **Sentinel Risk Index (SRI)**.

## Architecture Diagram

```mermaid
flowchart TD
    User([User]) --> Agent[AI Agent Gemini 2.5 Flash]
    Agent --> MCP[MCP Tool Requests]
    MCP -->|Action Logs / Tool Calls| SM[SentinelMCP Monitor]
    SM --> Interceptor[Sentinel Interceptor]
    Interceptor --> GraphBuilder[Behavior Graph Builder]
    GraphBuilder --> Context[Context Validator]
    Context --> Policy[Policy Validator]
    Policy --> RiskEngine[Sentinel Risk Engine]
    RiskEngine --> SRI[Sentinel Risk Index]
    SRI --> Decision{Decision Engine}
    Decision -->|SAFE / MONITOR| Tools[MCP Tools]
    Decision -->|SUSPICIOUS / BLOCKED| Dashboard[SentinelMCP Dashboard]
```

## Setup Instructions

This project requires **Python 3.10+**.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Project Layout Overview

```
.
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── ETHICS.md             # Ethical guidelines and data policies
├── README.md             # Project overview (this file)
├── requirements.txt      # Python dependencies
└── data/                 # Datasets
    └── attacks/
        └── set_a/        # Synthetic attack data (ignored except .gitkeep)
```

## Target Success Criteria

- F1 >= 0.80 on Set B, CI not crossing Policy-Only baseline.

## Compute Check Note

- Evaluation runs in < 15 mins on CPU.
