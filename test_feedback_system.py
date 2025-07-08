import os
import openai
from dotenv import load_dotenv
from ai_chess_agents import Agent

load_dotenv()

def test_human_feedback_system():
    """Test the human feedback system with sample agents"""
    
    # Set up OpenAI client
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        print("No OpenAI API key found. Please set OPENAI_API_KEY in your .env file.")
        return
    
    openai_client = openai.OpenAI(api_key=api_key)
    
    # Create test agents
    agent_alpha = Agent("Alpha", "aggressive", openai_client)
    agent_beta = Agent("Beta", "defensive", openai_client)
    
    # Add some mock game experience to their memory
    agent_alpha.memory.append({
        "type": "move",
        "turn": 1,
        "feeling": "confident",
        "move": "e2e4",
        "board": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "opponent_message": None,
        "goal": "Win the game",
        "subgoal": "Control the center",
        "values": agent_alpha.values.copy(),
        "timestamp": "2025-07-08 19:00:00"
    })
    
    agent_beta.memory.append({
        "type": "move",
        "turn": 2,
        "feeling": "focused",
        "move": "e7e5",
        "board": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
        "opponent_message": None,
        "goal": "Win the game",
        "subgoal": "Maintain solid position",
        "values": agent_beta.values.copy(),
        "timestamp": "2025-07-08 19:00:00"
    })
    
    print("🧠 AI CHESS AGENTS - HUMAN FEEDBACK SYSTEM TEST")
    print("=" * 60)
    print("This test demonstrates how agents interpret human feedback.")
    print()
    
    # Simulate human feedback
    print("📊 Simulating human feedback for Alpha (aggressive):")
    alpha_strategy = 7
    alpha_personality = 6
    alpha_comments = "Good aggressive play, but could be more patient in some positions."
    
    print(f"Strategy Rating: {alpha_strategy}/10")
    print(f"Personality Rating: {alpha_personality}/10")
    print(f"Comments: {alpha_comments}")
    print()
    
    print("📊 Simulating human feedback for Beta (defensive):")
    beta_strategy = 8
    beta_personality = 9
    beta_comments = "Excellent defensive play and very engaging personality!"
    
    print(f"Strategy Rating: {beta_strategy}/10")
    print(f"Personality Rating: {beta_personality}/10")
    print(f"Comments: {beta_comments}")
    print()
    
    print("🧠 Processing feedback with AI interpretation...")
    print()
    
    # Get AI interpretations
    alpha_interpretation = agent_alpha.interpret_human_feedback(
        alpha_strategy, alpha_personality, alpha_comments
    )
    
    beta_interpretation = agent_beta.interpret_human_feedback(
        beta_strategy, beta_personality, beta_comments
    )
    
    print(f"💭 Alpha's interpretation: {alpha_interpretation}")
    print()
    print(f"💭 Beta's interpretation: {beta_interpretation}")
    print()
    
    # Show updated values
    print("🔄 Updated Agent Values:")
    print(f"Alpha - Aggression: {agent_alpha.values['aggression_level']:.2f}, Creativity: {agent_alpha.values['creativity']:.2f}")
    print(f"Beta - Patience: {agent_beta.values['patience']:.2f}, Adaptability: {agent_beta.values['adaptability']:.2f}")
    print()
    
    # Save memories
    agent_alpha.save_memory()
    agent_beta.save_memory()
    
    print("💾 Agent memories saved with feedback data.")
    print("You can now run the web viewer to see the feedback in the game logs.")

if __name__ == "__main__":
    test_human_feedback_system() 