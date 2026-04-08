# 📈 CrowdWisdom Trading Agent API

A multi-agent AI system designed for prediction market analysis. This project scouts top-performing traders on Polymarket and Kalshi, enriches the data with live web context via Apify, and synthesizes copy-trading strategies using OpenRouter LLMs.

## 🚀 Features
* **Multi-Agent Architecture:** Modular scout agents for Polymarket (Gamma API) and Kalshi.
* **Retrieval-Augmented Generation (RAG):** Integrates Apify's Google Search Scraper for live real-world context on market events.
* **FastAPI Backend:** Fully interactive API with automatic Swagger UI documentation.
* **Interactive CLI Mode:** For quick terminal-based testing and interaction.
* **Closed Learning Loop:** Memory persistence to track feedback and improve future advice.

## 📂 Project Structure

```text
CROWDWISDOM-TRADING-AGENT/
├── crowdwisdom_agent/
│   ├── agents/               # Core agent logic
│   │   ├── chat_agent.py     # Main orchestrator
│   │   ├── kalshi_agent.py   # Kalshi API scout
│   │   ├── niche_agent.py    # LLM-based niche classifier
│   │   ├── polymarket_agent.py # Polymarket Gamma API scout
│   │   └── rag_agent.py      # Apify web enrichment
│   ├── api/                  # FastAPI endpoints
│   │   └── routes.py         
│   ├── core/                 # Shared utilities and configuration
│   │   ├── llm_client.py     # OpenRouter client wrapper
│   │   ├── logger.py         # Centralized logging
│   │   └── memory.py         # Learning loop persistence
│   ├── data/                 # Runtime data storage
│   ├── logs/                 # Application log files
│   ├── main.py               # Entry point (API & CLI)
│   └── requirements.txt      # Python dependencies
└── README.md

```

## 🛠️ Setup & Installation
### 1. Clone the repository
```bash
git clone [https://github.com/ananya0-0/crowdwisdom-trading-agent.git](https://github.com/ananya0-0/crowdwisdom-trading-agent.git)
cd crowdwisdom-trading-agent
```
### 2. Set up the virtual environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Environment Variables
```bash
OPENROUTER_API_KEY=your_openrouter_key_here
APIFY_API_TOKEN=your_apify_token_here
```

## 💻 Usage
### Option 1: Run the API Server
```bash
python main.py
```
### Option 2: Run the CLI
```bash
python main.py --cli
```



