# CrowdWisdom Trading Advisor

A modular, multi-agent AI system designed to analyze prediction markets (Polymarket & Kalshi), enrich data using Agentic RAG, and provide personalized copy-trading recommendations based on a closed-learning loop memory system.

This project was built as an internship assessment for CrowdWisdomTrading.

## 🧠 System Architecture

The project architecture is heavily inspired by the **Hermes Agent** framework, separating tool execution, LLM orchestration, and persistent memory into distinct, scalable modules.

The system utilizes a team of specialized agents:
1. **Scout Agents (`tools.py`):** Dedicated functions to extract top-performing, consistent wallets from Polymarket and Kalshi.
2. **Niche Agent (`agent.py`):** An LLM-powered classifier that analyzes a wallet's recent trade history to categorize their specific market niche (e.g., Sports, Politics, Crypto).
3. **RAG Agent (`tools.py`):** Utilizes the Apify Google Search Scraper API to fetch live, real-world context about the user's target event.
4. **Chat Advisor (`agent.py`):** The central orchestrator that synthesizes the scraped web data and the mapped trader profiles to deliver a final recommendation.

## 🔄 The Closed Learning Loop

To fulfill the requirement of a "closed learning loop," this system implements persistent memory tracking via `learning_loop_memory.json`. 

After every recommendation, the system prompts the user for feedback. This feedback is saved locally and dynamically injected into the Chat Agent's system prompt during all future interactions. This allows the agent to self-correct its copy-trading strategies and adapt to the user's risk tolerance over time without requiring manual code updates.

## 🛠️ Technology Stack

* **Language:** Python 3.10+
* **LLM Provider:** OpenRouter API (`meta-llama/llama-3.3-70b-instruct`)
* **RAG / Web Scraping:** Apify Client (`apify/google-search-scraper`)
* **Architecture:** Modular Agentic Framework

## 🚀 Quick Start Guide

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR-USERNAME/crowdwisdom-trading-agent.git](https://github.com/YOUR-USERNAME/crowdwisdom-trading-agent.git)
cd crowdwisdom-trading-agent
