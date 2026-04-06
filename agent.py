import os
import json
from openai import OpenAI
from tools import get_top_polymarket_traders, get_top_kalshi_traders, apify_research

class TradingAgent:
    def __init__(self):
        # OpenRouter SDK setup
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        # Using a fast, free/cheap model. You can change this to llama-3 or qwen.
        self.model = "meta-llama/llama-3.3-70b-instruct:free"
        
        
        # Closed Learning Loop setup
        self.memory_file = "learning_loop_memory.json"
        self.memory = self.load_memory()

    def load_memory(self):
        """Loads previous user feedback into the agent's memory."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {"lessons_learned": []}

    def save_memory(self):
        """Saves current feedback to disk for future sessions."""
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=4)

    def learn(self, feedback: str):
        """The core of the closed learning loop. Updates agent behavior."""
        self.memory["lessons_learned"].append(feedback)
        self.save_memory()
        print(f"\n[System] Memory updated. Agent learned: '{feedback}'")

    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Helper function to execute OpenRouter calls with memory injection."""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Inject the learning loop memory into the system context
        if self.memory["lessons_learned"]:
            memory_context = "\n- ".join(self.memory["lessons_learned"])
            messages.append({
                "role": "system", 
                "content": f"CRITICAL: Follow these past lessons from the user:\n- {memory_context}"
            })
            
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM API Error: {str(e)}"

    def map_niche(self, trader_data: list) -> str:
        """Niche Agent: Categorizes the trader's portfolio."""
        system = "You are a classifier agent. Look at the trader's recent trades and output ONLY ONE word representing their niche (e.g., Sports, Politics, Weather, Crypto)."
        return self.call_llm(system, str(trader_data)).strip()

    def get_advice(self, user_query: str):
        """The main orchestration flow."""
        print("-> [Scout Agent] Fetching top traders from Polymarket & Kalshi...")
        all_traders = get_top_polymarket_traders() + get_top_kalshi_traders()

        print("-> [Niche Agent] Mapping traders to specific niches...")
        for t in all_traders:
            t["niche"] = self.map_niche(t["recent_trades"])
            
        print(f"-> [RAG Agent] Researching current events for: {user_query} via Apify...")
        rag_context = apify_research(user_query)

        print("-> [Chat Agent] Formulating final advice...")
        system_prompt = f"""You are a prediction market copy-trading advisor. 
        Use the following live scraped context to understand the current event:
        {rag_context}
        
        Use the following mapped traders to recommend someone to copy:
        {json.dumps(all_traders, indent=2)}
        
        Recommend which trader the user should copy based on their query. Be concise."""
        
        return self.call_llm(system_prompt, user_query)