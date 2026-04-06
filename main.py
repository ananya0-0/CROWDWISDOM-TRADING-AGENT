from dotenv import load_dotenv
from agent import TradingAgent

def main():
    # Load environment variables from .env
    load_dotenv()
    
    # Initialize our AI Framework
    agent = TradingAgent()
    
    print("=========================================")
    print(" CrowdWisdom Trading Advisor Initialized ")
    print("=========================================")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
            
        # Execute the agent flow
        advice = agent.get_advice(user_input)
        print(f"\nAdvisor:\n{advice}\n")
        
        # Trigger the Closed Learning Loop
        print("-----------------------------------------")
        feedback = input("Did you like this advice? If not, tell me what to change next time (or press Enter to skip): ")
        if feedback.strip():
            agent.learn(feedback)

if __name__ == "__main__":
    main()