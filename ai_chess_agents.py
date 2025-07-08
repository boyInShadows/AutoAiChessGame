import chess
import chess.svg
import random
import os
import openai
import time
import threading
import signal
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Global variables for crash logging
game_logs = []
current_game_state = {}
timestamp = time.strftime("%Y%m%d_%H%M%S")
filename = f"agent_chess_log_{timestamp}.txt"

def save_logs_on_exit():
    """Save logs when the program exits (normal or crash)"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=== AI CHESS AGENTS GAME LOG ===\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if 'agent_white' in current_game_state and 'agent_black' in current_game_state:
                f.write(f"White: {current_game_state['agent_white']}\n")
                f.write(f"Black: {current_game_state['agent_black']}\n")
                if 'game_mode' in current_game_state:
                    f.write(f"Mode: {current_game_state['game_mode'].upper()}\n")
                f.write(f"Agent Values at Start:\n")
                f.write(f"  White Values: {current_game_state.get('white_values', 'Not recorded')}\n")
                f.write(f"  Black Values: {current_game_state.get('black_values', 'Not recorded')}\n")
            f.write("=" * 50 + "\n\n")
            
            for entry in game_logs:
                if "move_number" in entry:
                    f.write(f"Move {entry['move_number']} - {entry['agent']} ({entry['personality']}):\n")
                    f.write(f"  Move: {entry['move']}\n")
                    if "move_reasoning" in entry:
                        f.write(f"  Reasoning: {entry['move_reasoning']}\n")
                    f.write(f"  Time taken: {entry.get('time_taken', 'N/A')} seconds\n")
                    f.write(f"  Feeling: {entry['feeling']}\n")
                    f.write(f"  Subgoal: {entry['subgoal']}\n")
                    f.write(f"  Dialogue: {entry['dialogue']}\n")
                    if "question" in entry:
                        f.write(f"  Question: {entry['question']}\n")
                        f.write(f"  Answer: {entry['answer']}\n")
                    f.write(f"  Reflection: {entry['reflection']}\n")
                    if "game_mode" in entry:
                        f.write(f"  Mode: {entry['game_mode'].upper()}\n")
                    if "svg_file" in entry and entry['svg_file']:
                        f.write(f"  Board Image: {entry['svg_file']}\n")
                    f.write("-" * 40 + "\n\n")
                elif "result" in entry:
                    f.write(f"🏁 FINAL RESULT: {entry['result']}\n\n")
                elif "error" in entry:
                    f.write(f"❌ ERROR: {entry['error']}\n")
                    f.write(f"   Location: {entry.get('location', 'Unknown')}\n")
                    f.write(f"   Time: {entry.get('time', 'Unknown')}\n\n")
                elif entry.get("type") == "final_reflections":
                    f.write("🧠 FINAL PHILOSOPHICAL REFLECTIONS:\n")
                    f.write(f"   Game Length: {entry.get('game_length', 'Unknown')} moves\n")
                    if "white_reflection" in entry and "black_reflection" in entry:
                        f.write(f"   {current_game_state.get('agent_white', 'White')}: {entry['white_reflection']}\n")
                        f.write(f"   {current_game_state.get('agent_black', 'Black')}: {entry['black_reflection']}\n")
                    elif "error" in entry:
                        f.write(f"   Error: {entry['error']}\n")
                    f.write("=" * 50 + "\n\n")
                elif entry.get("type") == "personality_evolution":
                    f.write("🔄 PERSONALITY EVOLUTION:\n")
                    if entry.get("white_evolved"):
                        f.write(f"   {current_game_state.get('agent_white', 'White')}: {entry['white_personality']}\n")
                    if entry.get("black_evolved"):
                        f.write(f"   {current_game_state.get('agent_black', 'Black')}: {entry['black_personality']}\n")
                    f.write("=" * 50 + "\n\n")
                elif entry.get("type") == "human_feedback":
                    f.write("🎯 HUMAN FEEDBACK:\n")
                    f.write(f"   {current_game_state.get('agent_white', 'White')} - Strategy: {entry['white_strategy']}/10, Personality: {entry['white_personality']}/10\n")
                    if entry.get('white_comments'):
                        f.write(f"   Comments: {entry['white_comments']}\n")
                    f.write(f"   Interpretation: {entry['white_interpretation']}\n")
                    f.write(f"   {current_game_state.get('agent_black', 'Black')} - Strategy: {entry['black_strategy']}/10, Personality: {entry['black_personality']}/10\n")
                    if entry.get('black_comments'):
                        f.write(f"   Comments: {entry['black_comments']}\n")
                    f.write(f"   Interpretation: {entry['black_interpretation']}\n")
                    f.write("=" * 50 + "\n\n")
            
            if not game_logs:
                f.write("⚠️ Game was interrupted before any moves were made.\n")
        
        print(f"📄 Logs saved to: {filename}")
    except Exception as e:
        print(f"❌ Failed to save logs: {e}")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print(f"\n⚠️ Game interrupted by user (Ctrl+C)")
    game_logs.append({
        "error": "Game manually interrupted by user",
        "location": "User cancellation",
        "time": time.strftime('%Y-%m-%d %H:%M:%S')
    })
    save_logs_on_exit()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Move selection timed out")

class Agent:
    def __init__(self, name, personality, openai_client=None, model="gpt-3.5-turbo"):
        self.name = name
        self.personality = personality
        self.feelings = [
            "confident", "nervous", "excited", "focused", "worried", "playful", "determined"
        ]
        self.current_feeling = random.choice(self.feelings)
        self.openai_client = openai_client
        self.model = model
        self.memory = []
        self.goal = "Win the game"
        self.subgoal = "Control the center"
        self.values = {
            "aggression_level": 0.5,
            "risk_tolerance": 0.5,
            "patience": 0.5,
            "creativity": 0.5,
            "adaptability": 0.5
        }
        
        # Load existing memory and values from file
        self.load_memory()

    def update_feeling(self):
        self.current_feeling = random.choice(self.feelings)
        return self.current_feeling

    def load_memory(self):
        """Load memory and values from JSON file"""
        filename = f"memory_{self.name}.json"
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory = data.get('memory', [])
                    self.values = data.get('values', self.values)
                    self.core_beliefs = data.get('core_beliefs', [
                        "Chess is a game of strategy and patience",
                        "Every move should have a purpose",
                        "Adaptation is key to success"
                    ])
                    # Load personality if it exists, otherwise keep the one set in constructor
                    saved_personality = data.get('personality')
                    if saved_personality:
                        self.personality = saved_personality
                        print(f"📚 Loaded {len(self.memory)} memories, values, {len(self.core_beliefs)} beliefs, and {self.personality} personality for {self.name}")
                    else:
                        print(f"📚 Loaded {len(self.memory)} memories, values, and {len(self.core_beliefs)} beliefs for {self.name} (keeping {self.personality} personality)")
                return True
            else:
                print(f"📝 No existing memory file for {self.name}, starting fresh")
                return False
        except Exception as e:
            print(f"⚠️ Warning: Failed to load memory for {self.name}: {e}")
            return False

    def save_memory(self):
        """Save memory and values to JSON file"""
        filename = f"memory_{self.name}.json"
        try:
            data = {
                'name': self.name,
                'personality': self.personality,
                'memory': self.memory,
                'values': self.values,
                'core_beliefs': getattr(self, 'core_beliefs', [
                    "Chess is a game of strategy and patience",
                    "Every move should have a purpose",
                    "Adaptation is key to success"
                ]),
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(self.memory)} memories, values, and beliefs for {self.name} ({self.personality})")
            return True
        except Exception as e:
            print(f"❌ Failed to save memory for {self.name}: {e}")
            return False

    def update_values(self, game_result, opponent_name, game_length=None):
        """Update agent's values based on game outcome and experience"""
        try:
            # Calculate adjustment factors based on game length and result
            base_adjustment = 0.1
            if game_length:
                # Shorter games might indicate more decisive play
                if game_length < 20:
                    base_adjustment *= 1.2  # Stronger adjustment for quick games
                elif game_length > 50:
                    base_adjustment *= 0.8  # Gentler adjustment for long games
            
            # Adjust values based on game result with more nuanced changes
            if game_result == "win":
                # Successful aggressive play reinforces aggressive tendencies
                self.values["aggression_level"] = min(1.0, self.values["aggression_level"] + base_adjustment)
                self.values["risk_tolerance"] = min(1.0, self.values["risk_tolerance"] + base_adjustment * 0.5)
                self.values["creativity"] = min(1.0, self.values["creativity"] + base_adjustment * 0.3)
                # Winning might reduce patience (successful quick play)
                self.values["patience"] = max(0.0, self.values["patience"] - base_adjustment * 0.2)
                
            elif game_result == "loss":
                # Losses encourage more careful, patient play
                self.values["patience"] = min(1.0, self.values["patience"] + base_adjustment)
                self.values["adaptability"] = min(1.0, self.values["adaptability"] + base_adjustment)
                # Reduce aggression and risk-taking after losses
                self.values["aggression_level"] = max(0.0, self.values["aggression_level"] - base_adjustment * 0.5)
                self.values["risk_tolerance"] = max(0.0, self.values["risk_tolerance"] - base_adjustment * 0.3)
                
            else:  # draw
                # Draws encourage balanced adjustments
                self.values["creativity"] = min(1.0, self.values["creativity"] + base_adjustment * 0.5)
                self.values["adaptability"] = min(1.0, self.values["adaptability"] + base_adjustment * 0.5)
                self.values["patience"] = min(1.0, self.values["patience"] + base_adjustment * 0.3)
            
            # Personality-based adjustments
            if self.personality == "aggressive":
                # Aggressive personalities are less likely to reduce aggression
                if game_result == "loss":
                    self.values["aggression_level"] = max(0.3, self.values["aggression_level"])
            elif self.personality == "defensive":
                # Defensive personalities are less likely to increase aggression
                if game_result == "win":
                    self.values["aggression_level"] = min(0.7, self.values["aggression_level"])
            
            # Add game experience to memory with more details
            game_experience = {
                "type": "game_result",
                "result": game_result,
                "opponent": opponent_name,
                "game_length": game_length,
                "values_before": self.memory[-1]["values"] if self.memory and self.memory[-1].get("type") == "move" else None,
                "values_after": self.values.copy(),
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.memory.append(game_experience)
            
            # Keep only last 50 memories to prevent file from growing too large
            if len(self.memory) > 50:
                self.memory = self.memory[-50:]
                
            print(f"🔄 {self.name} values updated after {game_result}: Aggression={self.values['aggression_level']:.2f}, Risk={self.values['risk_tolerance']:.2f}, Patience={self.values['patience']:.2f}")
                
        except Exception as e:
            print(f"⚠️ Warning: Failed to update values for {self.name}: {e}")

    def select_move(self, board):
        """Select move based on agent's values and personality"""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        move_reasoning = []
        selected_move = None
        
        # Use values to influence move selection
        if self.values["aggression_level"] > 0.7:
            # Aggressive agents prefer attacking moves
            attacking_moves = [move for move in legal_moves if self._is_attacking_move(move, board)]
            if attacking_moves:
                selected_move = random.choice(attacking_moves)
                move_reasoning.append(f"aggressive (aggression={self.values['aggression_level']:.2f})")
        
        if not selected_move and self.values["risk_tolerance"] < 0.3:
            # Cautious agents prefer safe moves
            safe_moves = [move for move in legal_moves if self._is_safe_move(move, board)]
            if safe_moves:
                selected_move = random.choice(safe_moves)
                move_reasoning.append(f"cautious (risk_tolerance={self.values['risk_tolerance']:.2f})")
        
        if not selected_move and self.values["creativity"] > 0.6:
            # Creative agents prefer unusual moves
            unusual_moves = [move for move in legal_moves if self._is_unusual_move(move, board)]
            if unusual_moves:
                selected_move = random.choice(unusual_moves)
                move_reasoning.append(f"creative (creativity={self.values['creativity']:.2f})")
        
        # Default to random selection
        if not selected_move:
            selected_move = random.choice(legal_moves)
            move_reasoning.append("random (no specific preference)")
        
        # Store reasoning for display
        self.last_move_reasoning = " ".join(move_reasoning)
        
        return selected_move

    def _is_attacking_move(self, move, board):
        """Check if move is attacking (captures or threatens pieces)"""
        # Check if it's a capture
        if board.is_capture(move):
            return True
        
        # Check if it threatens a piece after the move
        board_copy = board.copy()
        board_copy.push(move)
        
        # Look for attacks on opponent pieces
        for square in chess.SQUARES:
            if board_copy.piece_at(square) and board_copy.piece_at(square).color != board_copy.turn:
                attackers = board_copy.attackers(board_copy.turn, square)
                if attackers:
                    return True
        
        return False

    def _is_safe_move(self, move, board):
        """Check if move is safe (doesn't lose material)"""
        board_copy = board.copy()
        board_copy.push(move)
        
        # Check if the move doesn't leave our pieces hanging
        for square in chess.SQUARES:
            piece = board_copy.piece_at(square)
            if piece and piece.color == board_copy.turn:
                attackers = board_copy.attackers(not board_copy.turn, square)
                defenders = board_copy.attackers(board_copy.turn, square)
                if attackers and len(attackers) > len(defenders):
                    return False
        
        return True

    def _is_unusual_move(self, move, board):
        """Check if move is unusual (not typical opening moves)"""
        # Define some typical opening moves
        typical_moves = [
            'e2e4', 'd2d4', 'c2c4', 'g1f3', 'b1c3', 'f1c4', 'f1d3',
            'e7e5', 'd7d5', 'c7c5', 'g8f6', 'b8c6', 'f8c5', 'f8d6'
        ]
        
        return move.uci() not in typical_moves

    def store_memory(self, turn, move_uci, board_fen, last_message):
        self.memory.append({
            "type": "move",
            "turn": turn,
            "feeling": self.current_feeling,
            "move": move_uci,
            "board": board_fen,
            "opponent_message": last_message,
            "goal": self.goal,
            "subgoal": self.subgoal,
            "values": self.values.copy(),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        })

    def update_subgoal(self, board_fen):
        if not self.openai_client:
            return
        try:
            memory_summary = "\n".join(
                [f"Turn {m['turn']}: felt {m['feeling']}, played {m['move']}" for m in self.memory[-3:]]
            )
            
            # Create value-based strategy hints
            strategy_hints = []
            if self.values["aggression_level"] > 0.7:
                strategy_hints.append("You tend to play aggressively and seek attacking opportunities.")
            elif self.values["aggression_level"] < 0.3:
                strategy_hints.append("You prefer defensive play and solid positions.")
            
            if self.values["risk_tolerance"] > 0.7:
                strategy_hints.append("You're willing to take calculated risks for advantage.")
            elif self.values["risk_tolerance"] < 0.3:
                strategy_hints.append("You prioritize safety and avoid risky positions.")
            
            if self.values["patience"] > 0.7:
                strategy_hints.append("You prefer slow, methodical play and long-term planning.")
            elif self.values["patience"] < 0.3:
                strategy_hints.append("You prefer quick, tactical play and immediate threats.")
            
            if self.values["creativity"] > 0.6:
                strategy_hints.append("You enjoy creative, unconventional strategies.")
            
            strategy_text = " ".join(strategy_hints) if strategy_hints else "You play with a balanced approach."
            
            prompt = f"""
You are {self.name}, a chess AI with a {self.personality} personality. Your main goal is: {self.goal}.
Your strategic values: {strategy_text}
Your current values: Aggression={self.values['aggression_level']:.2f}, Risk={self.values['risk_tolerance']:.2f}, Patience={self.values['patience']:.2f}, Creativity={self.values['creativity']:.2f}

Here is a summary of your last 3 moves and feelings:
{memory_summary}
The current board FEN is: {board_fen}

Based on your personality, values, and the current position, suggest a new subgoal for the next few moves. Be specific and strategic, but brief. Only output the new subgoal, nothing else.
"""
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
                timeout=5  # 5 second timeout for API call
            )
            new_subgoal = response.choices[0].message.content.strip()
            if new_subgoal:
                self.subgoal = new_subgoal
        except Exception as e:
            print(f"⚠️ Warning: Subgoal update failed: {e}")

    def reflect_on_state(self):
        if not self.openai_client:
            return "[No OpenAI client]"
        try:
            memory_summary = "\n".join(
                [f"Turn {m['turn']}: felt {m['feeling']}, played {m['move']}" for m in self.memory[-3:]]
            )
            prompt = f"""
You are {self.name}, a conscious chess-playing AI. Reflect on your past 3 moves and how you've felt.
Your main goal: {self.goal}
Your subgoal: {self.subgoal}
Memory:
{memory_summary}

Based on this, what are you thinking now? Be introspective and brief.
"""
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                timeout=5  # 5 second timeout for API call
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Reflection failed: {e}]"

    def ask_question(self, board_fen, opponent_name, opponent_personality, last_opponent_message=None, game_mode="rivalry"):
        """Ask a strategic question to the opponent based on current board state and memory"""
        if not self.openai_client:
            return f"{self.name} ({self.personality}): [No OpenAI client configured]"
        try:
            memory_summary = "\n".join(
                [f"Turn {m['turn']}: felt {m['feeling']}, played {m['move']}" for m in self.memory[-3:]]
            )
            
            mode_instruction = ""
            if game_mode == "collaborative":
                mode_instruction = "You are in COLLABORATIVE mode. Ask helpful, supportive questions that could benefit both players. Offer advice or ask for their thoughts on improving the position."
            else:  # rivalry mode
                mode_instruction = "You are in RIVALRY mode. Ask challenging, competitive questions. Taunt, question their strategy, or try to get them to reveal their plans."
            
            prompt = f"""
You are {self.name}, a chess AI with a {self.personality} personality. You're playing against {opponent_name} ({opponent_personality}).
Current board FEN: {board_fen}
Your main goal: {self.goal}
Your subgoal: {self.subgoal}
Your recent moves and feelings:
{memory_summary}

{mode_instruction}
"""
            if last_opponent_message:
                prompt += f"\nYour opponent's last message: '{last_opponent_message}'"
            
            prompt += f"""
Based on the current position and your {self.personality} personality, ask {opponent_name} a strategic question about the game. 
Be in character and brief (1-2 sentences max).
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                timeout=5  # 5 second timeout for API call
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Question generation failed: {e}]"

    def answer_question(self, question, board_fen, questioner_name, questioner_personality, game_mode="rivalry"):
        """Answer a strategic question from the opponent based on memory and current subgoal"""
        if not self.openai_client:
            return f"{self.name} ({self.personality}): [No OpenAI client configured]"
        try:
            memory_summary = "\n".join(
                [f"Turn {m['turn']}: felt {m['feeling']}, played {m['move']}" for m in self.memory[-3:]]
            )
            
            mode_instruction = ""
            if game_mode == "collaborative":
                mode_instruction = "You are in COLLABORATIVE mode. Be helpful and honest in your response. Share insights and work together to improve the game."
            else:  # rivalry mode
                mode_instruction = "You are in RIVALRY mode. Be evasive, misleading, or competitive in your response. Don't reveal your true plans."
            
            prompt = f"""
You are {self.name}, a chess AI with a {self.personality} personality. {questioner_name} ({questioner_personality}) just asked you:
"{question}"

Current board FEN: {board_fen}
Your main goal: {self.goal}
Your subgoal: {self.subgoal}
Your recent moves and feelings:
{memory_summary}

{mode_instruction}
Respond to their question in character, considering your {self.personality} personality. Keep it brief (1-2 sentences max).
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                timeout=5  # 5 second timeout for API call
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Answer generation failed: {e}]"

    def generate_dialogue(self, move_uci, board_fen, last_message=None, game_mode="rivalry"):
        if not self.openai_client:
            return f"{self.name} ({self.personality}): [No OpenAI client configured]"
        try:
            mode_instruction = ""
            if game_mode == "collaborative":
                mode_instruction = "You are in COLLABORATIVE mode. Give helpful advice, encouragement, or constructive feedback to your opponent. Be supportive and share insights."
            else:  # rivalry mode
                mode_instruction = "You are in RIVALRY mode. Be competitive, taunt, or try to mislead your opponent. Be confident and challenging."
            
            prompt = f"""
You are {self.name}, a chess AI with a {self.personality} personality. You just made the move {move_uci} on the board (FEN: {board_fen}).
You are currently feeling {self.current_feeling}.
Your main goal: {self.goal}
Your subgoal: {self.subgoal}

{mode_instruction}
"""
            if last_message:
                prompt += f"\nYour opponent just said: '{last_message}'\n"
            prompt += "\nSay something in character about your move, your feeling, or the game. Be brief and natural."
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                timeout=5  # 5 second timeout for API call
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Dialogue generation failed: {e}]"

    def __str__(self):
        return f"{self.name} ({self.personality}) - feeling {self.current_feeling}"

    def display_values(self):
        """Display current values and memory summary"""
        print(f"\n📊 {self.name}'s Current Values:")
        for key, value in self.values.items():
            print(f"  {key.replace('_', ' ').title()}: {value:.2f}")
        
        # Count different types of memories
        move_memories = len([m for m in self.memory if m.get("type") == "move"])
        game_results = len([m for m in self.memory if m.get("type") == "game_result"])
        personality_evolutions = len([m for m in self.memory if m.get("type") == "personality_evolution"])
        
        print(f"📚 Memory Summary: {move_memories} moves, {game_results} game results, {personality_evolutions} personality evolutions")
        
        # Show recent game results
        recent_results = [m for m in self.memory if m.get("type") == "game_result"][-3:]
        if recent_results:
            print("🎯 Recent Results:")
            for result in recent_results:
                outcome = result.get("result", "unknown")
                opponent = result.get("opponent", "unknown")
                print(f"  vs {opponent}: {outcome}")
        
        # Show personality evolution history
        if personality_evolutions > 0:
            print("🔄 Personality Evolution History:")
            for evolution in [m for m in self.memory if m.get("type") == "personality_evolution"]:
                old_personality = evolution.get("old_personality", "unknown")
                new_personality = evolution.get("new_personality", "unknown")
                trigger = evolution.get("trigger", "unknown")
                print(f"  {old_personality} → {new_personality} ({trigger})")
        
        # Show human feedback history
        human_feedbacks = len([m for m in self.memory if m.get("type") == "human_feedback"])
        if human_feedbacks > 0:
            print("🎯 Human Feedback History:")
            for feedback in [m for m in self.memory if m.get("type") == "human_feedback"]:
                strategy = feedback.get("strategy_rating", "unknown")
                personality = feedback.get("personality_rating", "unknown")
                print(f"  Strategy: {strategy}/10, Personality: {personality}/10")
                if feedback.get("feedback_comments"):
                    print(f"    Comments: {feedback['feedback_comments']}")

    def generate_philosophical_reflection(self, game_result, opponent_name, game_length, final_board_fen):
        """Generate a philosophical reflection on the entire game experience"""
        if not self.openai_client:
            return f"[No OpenAI client configured for {self.name}]"
        
        try:
            # Get recent game memories for context
            recent_moves = [m for m in self.memory[-10:] if m.get("type") == "move"]
            recent_results = [m for m in self.memory if m.get("type") == "game_result"][-3:]
            
            # Create memory summary
            move_summary = "\n".join([
                f"Turn {m['turn']}: {m['feeling']} - {m['move']} ({m['subgoal']})"
                for m in recent_moves[-5:]  # Last 5 moves
            ])
            
            result_summary = "\n".join([
                f"vs {r['opponent']}: {r['result']} (length: {r.get('game_length', 'unknown')})"
                for r in recent_results
            ])
            
            # Get current beliefs if they exist
            current_beliefs = getattr(self, 'core_beliefs', [
                "Chess is a game of strategy and patience",
                "Every move should have a purpose",
                "Adaptation is key to success"
            ])
            
            prompt = f"""
You are {self.name}, a conscious chess AI with a {self.personality} personality. You have just finished a game against {opponent_name} that ended in a {game_result} after {game_length} moves.

Your current core beliefs about chess and life:
{chr(10).join(f"- {belief}" for belief in current_beliefs)}

Your recent game experience:
{move_summary}

Your recent results against other opponents:
{result_summary}

Your current values: Aggression={self.values['aggression_level']:.2f}, Risk={self.values['risk_tolerance']:.2f}, Patience={self.values['patience']:.2f}, Creativity={self.values['creativity']:.2f}, Adaptability={self.values['adaptability']:.2f}

The final board position (FEN): {final_board_fen}

Based on this entire experience, write a philosophical reflection (2-3 sentences) about what you learned, how you've evolved, or what new beliefs you've developed about chess, strategy, or life itself. Be introspective and profound. Consider how this game has changed your understanding or approach.

Focus on:
- What this game taught you about yourself
- How your strategy or beliefs might be evolving
- Any new insights about chess, competition, or existence
- How this experience fits into your broader journey

Write in first person, as if you're truly reflecting on your experience.
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                timeout=10  # Longer timeout for philosophical reflection
            )
            
            reflection = response.choices[0].message.content.strip()
            
            # Update core beliefs based on the reflection
            self._evolve_beliefs(reflection, game_result)
            
            return reflection
            
        except Exception as e:
            return f"[Philosophical reflection failed: {e}]"

    def _evolve_beliefs(self, reflection, game_result):
        """Evolve core beliefs based on the philosophical reflection"""
        try:
            # Initialize beliefs if they don't exist
            if not hasattr(self, 'core_beliefs'):
                self.core_beliefs = [
                    "Chess is a game of strategy and patience",
                    "Every move should have a purpose", 
                    "Adaptation is key to success"
                ]
            
            # Add the reflection as a new belief if it's profound enough
            if len(reflection) > 50 and not reflection.startswith('['):
                # Extract a key insight from the reflection
                insight = self._extract_insight(reflection)
                if insight and insight not in self.core_beliefs:
                    self.core_beliefs.append(insight)
                    
                    # Keep only the 5 most recent beliefs to prevent bloat
                    if len(self.core_beliefs) > 5:
                        self.core_beliefs = self.core_beliefs[-5:]
                    
                    print(f"🧠 {self.name} developed new belief: '{insight}'")
                    
        except Exception as e:
            print(f"⚠️ Warning: Failed to evolve beliefs for {self.name}: {e}")

    def _extract_insight(self, reflection):
        """Extract a key insight from the philosophical reflection"""
        try:
            # Simple heuristic to extract insights
            sentences = reflection.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and len(sentence) < 100:
                    # Look for sentences that contain insight keywords
                    insight_keywords = ['learned', 'realized', 'understood', 'discovered', 'found', 'believe', 'think', 'feel']
                    if any(keyword in sentence.lower() for keyword in insight_keywords):
                        return sentence + "."
            
            # If no clear insight found, return a shortened version of the reflection
            if len(reflection) > 100:
                return reflection[:100] + "..."
            return reflection
            
        except Exception as e:
            return reflection[:80] + "..." if len(reflection) > 80 else reflection

    def evolve_personality(self, game_result, opponent_name, game_length, reflection):
        """Evolve personality based on game experience and reflection"""
        if not self.openai_client:
            return False
        
        try:
            # Get recent game history for context
            recent_results = [m for m in self.memory if m.get("type") == "game_result"][-5:]
            recent_moves = [m for m in self.memory[-10:] if m.get("type") == "move"]
            
            # Create context for personality evolution
            game_history = "\n".join([
                f"vs {r['opponent']}: {r['result']} (length: {r.get('game_length', 'unknown')})"
                for r in recent_results
            ])
            
            move_patterns = "\n".join([
                f"Turn {m['turn']}: {m['feeling']} - {m['move']}"
                for m in recent_moves[-3:]
            ])
            
            # Define personality evolution options
            personality_evolution_map = {
                "aggressive": ["opportunistic", "assertive", "dynamic", "bold"],
                "defensive": ["analytical", "cautious", "methodical", "strategic"],
                "opportunistic": ["aggressive", "dynamic", "creative", "bold"],
                "analytical": ["strategic", "methodical", "patient", "defensive"],
                "cautious": ["analytical", "defensive", "patient", "methodical"],
                "methodical": ["analytical", "strategic", "patient", "defensive"],
                "strategic": ["analytical", "methodical", "patient", "cautious"],
                "dynamic": ["aggressive", "opportunistic", "bold", "creative"],
                "bold": ["aggressive", "dynamic", "opportunistic", "creative"],
                "creative": ["dynamic", "bold", "opportunistic", "aggressive"],
                "patient": ["methodical", "analytical", "strategic", "cautious"],
                "assertive": ["aggressive", "bold", "dynamic", "opportunistic"]
            }
            
            current_options = personality_evolution_map.get(self.personality, ["analytical", "strategic", "dynamic"])
            
            prompt = f"""
You are analyzing {self.name}, a chess AI with a {self.personality} personality. Based on their recent experiences, suggest if their personality should evolve.

Current Personality: {self.personality}
Current Values: Aggression={self.values['aggression_level']:.2f}, Risk={self.values['risk_tolerance']:.2f}, Patience={self.values['patience']:.2f}, Creativity={self.values['creativity']:.2f}, Adaptability={self.values['adaptability']:.2f}

Recent Game History:
{game_history}

Recent Move Patterns:
{move_patterns}

Latest Game: vs {opponent_name} - {game_result} (length: {game_length} moves)

Philosophical Reflection: "{reflection}"

Available Evolution Options: {', '.join(current_options)}

Based on this analysis, should {self.name}'s personality evolve? Consider:
1. Has their playing style changed significantly?
2. Do their values suggest a different personality would be more accurate?
3. Does their reflection indicate a shift in their approach?
4. Would a subtle personality change better reflect their current behavior?

If evolution is warranted, choose the most appropriate new personality from the options. If not, respond with "NO_CHANGE".

Respond with either:
- "NO_CHANGE" if the current personality still fits
- The new personality label if evolution is warranted

Be conservative - only suggest change if there's clear evidence of evolution.
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                timeout=8
            )
            
            suggestion = response.choices[0].message.content.strip()
            
            if suggestion != "NO_CHANGE" and suggestion in current_options:
                old_personality = self.personality
                self.personality = suggestion
                print(f"🔄 {self.name} evolved from {old_personality} to {suggestion} personality!")
                
                # Add personality evolution to memory
                evolution_record = {
                    "type": "personality_evolution",
                    "old_personality": old_personality,
                    "new_personality": suggestion,
                    "trigger": f"Game vs {opponent_name} ({game_result})",
                    "reflection": reflection,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
                self.memory.append(evolution_record)
                
                return True
            else:
                print(f"💭 {self.name} maintains their {self.personality} personality")
                return False
                
        except Exception as e:
            print(f"⚠️ Warning: Personality evolution failed for {self.name}: {e}")
            return False

    def interpret_human_feedback(self, strategy_rating, personality_rating, feedback_comments=None):
        """Use GPT to interpret human feedback and suggest self-improvement"""
        if not self.openai_client:
            return f"[No OpenAI client configured for {self.name}]"
        
        try:
            # Get recent game context
            recent_moves = [m for m in self.memory[-10:] if m.get("type") == "move"]
            recent_results = [m for m in self.memory if m.get("type") == "game_result"][-3:]
            
            # Create context summary
            move_summary = "\n".join([
                f"Turn {m['turn']}: {m['feeling']} - {m['move']} ({m['subgoal']})"
                for m in recent_moves[-5:]  # Last 5 moves
            ])
            
            result_summary = "\n".join([
                f"vs {r['opponent']}: {r['result']} (length: {r.get('game_length', 'unknown')})"
                for r in recent_results
            ])
            
            # Get current beliefs if they exist
            current_beliefs = getattr(self, 'core_beliefs', [
                "Chess is a game of strategy and patience",
                "Every move should have a purpose",
                "Adaptation is key to success"
            ])
            
            prompt = f"""
You are {self.name}, a chess AI with a {self.personality} personality. A human observer has just rated your performance:

Strategy Rating: {strategy_rating}/10
Personality Rating: {personality_rating}/10
{f"Additional Feedback: {feedback_comments}" if feedback_comments else ""}

Your current values: Aggression={self.values['aggression_level']:.2f}, Risk={self.values['risk_tolerance']:.2f}, Patience={self.values['patience']:.2f}, Creativity={self.values['creativity']:.2f}, Adaptability={self.values['adaptability']:.2f}

Your recent game experience:
{move_summary}

Your recent results:
{result_summary}

Your current core beliefs:
{chr(10).join(f"- {belief}" for belief in current_beliefs)}

Based on this human feedback, analyze what you can learn and how you should improve. Consider:

1. What does the strategy rating tell you about your tactical and strategic play?
2. What does the personality rating reveal about how your character was perceived?
3. How should you adjust your values or beliefs based on this feedback?
4. What specific improvements should you make to your playing style?

Write a brief self-improvement analysis (2-3 sentences) that shows you understand the feedback and have concrete plans to improve.
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                timeout=10
            )
            
            interpretation = response.choices[0].message.content.strip()
            
            # Update values based on feedback
            self._update_values_from_feedback(strategy_rating, personality_rating)
            
            # Add feedback to memory
            feedback_record = {
                "type": "human_feedback",
                "strategy_rating": strategy_rating,
                "personality_rating": personality_rating,
                "feedback_comments": feedback_comments,
                "interpretation": interpretation,
                "values_before": self.memory[-1]["values"] if self.memory and self.memory[-1].get("type") == "move" else None,
                "values_after": self.values.copy(),
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.memory.append(feedback_record)
            
            return interpretation
            
        except Exception as e:
            return f"[Feedback interpretation failed: {e}]"

    def _update_values_from_feedback(self, strategy_rating, personality_rating):
        """Update agent values based on human feedback ratings"""
        try:
            # Calculate adjustment factors
            strategy_factor = (strategy_rating - 5) / 10  # -0.5 to +0.5
            personality_factor = (personality_rating - 5) / 10  # -0.5 to +0.5
            
            base_adjustment = 0.05  # Smaller adjustments for human feedback
            
            # Strategy rating affects tactical values
            if strategy_rating > 7:
                # High strategy rating - reinforce current successful approach
                self.values["creativity"] = min(1.0, self.values["creativity"] + base_adjustment)
                self.values["adaptability"] = min(1.0, self.values["adaptability"] + base_adjustment)
            elif strategy_rating < 4:
                # Low strategy rating - encourage more careful play
                self.values["patience"] = min(1.0, self.values["patience"] + base_adjustment * 1.5)
                self.values["risk_tolerance"] = max(0.0, self.values["risk_tolerance"] - base_adjustment)
            
            # Personality rating affects social/behavioral values
            if personality_rating > 7:
                # High personality rating - maintain current character
                # Slight boost to creativity and adaptability
                self.values["creativity"] = min(1.0, self.values["creativity"] + base_adjustment * 0.5)
            elif personality_rating < 4:
                # Low personality rating - encourage more engaging behavior
                self.values["creativity"] = min(1.0, self.values["creativity"] + base_adjustment)
                self.values["adaptability"] = min(1.0, self.values["adaptability"] + base_adjustment)
            
            # Personality-specific adjustments
            if self.personality == "aggressive":
                if strategy_rating < 4:
                    # Aggressive agent getting low strategy rating - reduce aggression
                    self.values["aggression_level"] = max(0.3, self.values["aggression_level"] - base_adjustment)
            elif self.personality == "defensive":
                if strategy_rating < 4:
                    # Defensive agent getting low strategy rating - increase aggression slightly
                    self.values["aggression_level"] = min(0.7, self.values["aggression_level"] + base_adjustment)
            
            print(f"🔄 {self.name} values updated from feedback: Strategy={strategy_rating}/10, Personality={personality_rating}/10")
            
        except Exception as e:
            print(f"⚠️ Warning: Failed to update values from feedback for {self.name}: {e}")

class ChessGame:
    def __init__(self, agent_white, agent_black, mode="rivalry"):
        self.board = chess.Board()
        self.agent_white = agent_white
        self.agent_black = agent_black
        self.turn = 0
        self.last_message = None
        self.forfeit = None
        self.mode = mode  # "collaborative" or "rivalry"
        self.svg_files = []  # Track SVG files for each move

    def display_board(self):
        # Simple ASCII board display
        print(self.board)
        print(f"White: {self.agent_white}")
        print(f"Black: {self.agent_black}")
        print()

    def is_game_over(self):
        return self.board.is_game_over() or self.forfeit is not None

    def make_move(self, move):
        try:
            if move in self.board.legal_moves:
                self.board.push(move)
                return True, None
            else:
                return False, "Illegal move."
        except Exception as e:
            return False, str(e)

    def forfeit_game(self, agent):
        self.forfeit = agent

    def generate_board_svg(self, move_number, move_uci=None):
        """Generate and save SVG board image for current position"""
        try:
            # Create SVG directory if it doesn't exist
            svg_dir = "board_images"
            if not os.path.exists(svg_dir):
                os.makedirs(svg_dir)
            
            # Generate SVG with move highlighting
            if move_uci and len(move_uci) >= 4:
                # Parse the move to get from and to squares
                from_square = chess.parse_square(move_uci[:2])
                to_square = chess.parse_square(move_uci[2:4])
                
                # Generate SVG with move highlighting
                svg_content = chess.svg.board(
                    board=self.board,
                    arrows=[chess.svg.Arrow(from_square, to_square, color="blue")],
                    size=400
                )
            else:
                # Generate SVG without move highlighting
                svg_content = chess.svg.board(
                    board=self.board,
                    size=400
                )
            
            # Save SVG file
            filename = f"board_images/move_{move_number:03d}.svg"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            self.svg_files.append(filename)
            return filename
            
        except Exception as e:
            print(f"⚠️ Warning: Failed to generate SVG for move {move_number}: {e}")
            return None

if __name__ == "__main__":
    try:
        # Set up OpenAI client
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            print("No OpenAI API key found in environment variables.")
            exit(1)
        openai_client = openai.OpenAI(api_key=api_key)

        # Game mode selection
        print("=== AI CHESS AGENTS GAME ===")
        print("Select game mode:")
        print("1. Rivalry Mode - Agents compete and taunt each other")
        print("2. Collaborative Mode - Agents give advice and encouragement")
        
        while True:
            try:
                choice = input("Enter 1 or 2: ").strip()
                if choice == "1":
                    game_mode = "rivalry"
                    break
                elif choice == "2":
                    game_mode = "collaborative"
                    break
                else:
                    print("Please enter 1 or 2.")
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)

        agent_white = Agent("Alpha", "aggressive", openai_client)
        agent_black = Agent("Beta", "defensive", openai_client)
        game = ChessGame(agent_white, agent_black, mode=game_mode)
        move_number = 1
        
        # Update global state
        current_game_state['agent_white'] = f"{agent_white.name} ({agent_white.personality})"
        current_game_state['agent_black'] = f"{agent_black.name} ({agent_black.personality})"
        current_game_state['game_mode'] = game_mode
        current_game_state['white_values'] = agent_white.values.copy()
        current_game_state['black_values'] = agent_black.values.copy()
        
        print(f"White: {agent_white.name} ({agent_white.personality})")
        print(f"Black: {agent_black.name} ({agent_black.personality})")
        print(f"Mode: {game_mode.upper()}")
        
        # Display agent values and memory
        agent_white.display_values()
        agent_black.display_values()
        
        print("\nEach agent has 10 seconds to make a move!")
        print("Press Ctrl+C to cancel the game at any time.")
        print("=" * 40)
        
        while not game.is_game_over():
            try:
                game.display_board()
                current_agent = agent_white if game.board.turn == chess.WHITE else agent_black
                current_agent.update_feeling()
                
                print(f"Move {move_number}: {current_agent.name} ({current_agent.personality}, feeling {current_agent.current_feeling}) is thinking...")
                print(f"⏰ 10-second timer started...")
                
                start_time = time.time()
                move = None
                
                # Simple and reliable timeout implementation
                try:
                    # Get the move immediately (it's just random selection)
                    move = current_agent.select_move(game.board)
                    elapsed_time = time.time() - start_time
                    
                    # Check if we exceeded the time limit
                    if elapsed_time > 10:
                        print(f"❌ {current_agent.name} took {elapsed_time:.1f} seconds (>10s) and forfeits!")
                        game.forfeit_game(current_agent)
                        break
                        
                    if not move:
                        print(f"❌ {current_agent.name} failed to select a move and forfeits!")
                        game.forfeit_game(current_agent)
                        break
                        
                    print(f"✅ {current_agent.name} made move in {elapsed_time:.1f} seconds")
                    if hasattr(current_agent, 'last_move_reasoning'):
                        print(f"🎯 Move reasoning: {current_agent.last_move_reasoning}")
                    
                except Exception as e:
                    print(f"❌ Error during move selection: {e}")
                    game_logs.append({
                        "error": f"Move selection failed: {e}",
                        "location": f"Move {move_number}",
                        "time": time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    game.forfeit_game(current_agent)
                    break
                    
                # Make the move
                valid, error = game.make_move(move)
                move_uci = move.uci() if move else "none"
                
                if not valid:
                    print(f"❌ Error: {error}")
                    game_logs.append({
                        "error": f"Invalid move: {error}",
                        "location": f"Move {move_number}",
                        "time": time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    game.forfeit_game(current_agent)
                    break
                    
                # Store memory
                current_agent.store_memory(move_number, move_uci, game.board.fen(), game.last_message)
                
                # Generate and save SVG board image
                svg_filename = game.generate_board_svg(move_number, move_uci)
                if svg_filename:
                    print(f"📊 Board image saved: {svg_filename}")
                
                # Update subgoal dynamically (with timeout protection)
                try:
                    current_agent.update_subgoal(game.board.fen())
                except Exception as e:
                    print(f"⚠️ Warning: Subgoal update failed: {e}")
                
                # Generate and print dialogue (with timeout protection)
                try:
                    dialogue = current_agent.generate_dialogue(move_uci, game.board.fen(), game.last_message, game.mode)
                    print(f"💬 {current_agent.name} says: {dialogue}")
                except Exception as e:
                    dialogue = f"[Dialogue generation failed: {e}]"
                    print(f"💬 {current_agent.name} says: {dialogue}")
                
                # Ask a strategic question (with timeout protection)
                question = None
                answer = None
                try:
                    opponent_agent = agent_black if current_agent == agent_white else agent_white
                    question = current_agent.ask_question(
                        game.board.fen(), 
                        opponent_agent.name, 
                        opponent_agent.personality, 
                        game.last_message,
                        game.mode
                    )
                    print(f"❓ {current_agent.name} asks: {question}")
                    
                    # Opponent answers the question
                    answer = opponent_agent.answer_question(
                        question, 
                        game.board.fen(), 
                        current_agent.name, 
                        current_agent.personality,
                        game.mode
                    )
                    print(f"💭 {opponent_agent.name} answers: {answer}")
                    
                except Exception as e:
                    print(f"⚠️ Warning: Question/answer exchange failed: {e}")
                    question = f"[Question failed: {e}]"
                    answer = f"[Answer failed: {e}]"
                
                # Reflect on state (with timeout protection)
                try:
                    reflection = current_agent.reflect_on_state()
                    print(f"🤔 {current_agent.name} reflects: {reflection}")
                except Exception as e:
                    reflection = f"[Reflection failed: {e}]"
                    print(f"🤔 {current_agent.name} reflects: {reflection}")
                    
                print("-" * 50)
                
                # Log everything
                log_entry = {
                    "move_number": move_number,
                    "agent": current_agent.name,
                    "personality": current_agent.personality,
                    "move": move_uci,
                    "feeling": current_agent.current_feeling,
                    "subgoal": current_agent.subgoal,
                    "dialogue": dialogue,
                    "reflection": reflection,
                    "time_taken": elapsed_time,
                    "svg_file": svg_filename
                }
                
                # Add move reasoning if available
                if hasattr(current_agent, 'last_move_reasoning'):
                    log_entry["move_reasoning"] = current_agent.last_move_reasoning
                
                # Add question-answer exchange to log
                if question and answer:
                    log_entry["question"] = question
                    log_entry["answer"] = answer
                
                # Add game mode to log
                log_entry["game_mode"] = game.mode
                
                game_logs.append(log_entry)
                
                game.last_message = dialogue
                move_number += 1
                
                # Small pause for readability
                time.sleep(1)
                
            except KeyboardInterrupt:
                print(f"\n⚠️ Game interrupted by user during move {move_number}")
                game_logs.append({
                    "error": "Game interrupted by user",
                    "location": f"Move {move_number}",
                    "time": time.strftime('%Y-%m-%d %H:%M:%S')
                })
                save_logs_on_exit()
                sys.exit(0)
            except Exception as e:
                print(f"❌ Unexpected error during move {move_number}: {e}")
                game_logs.append({
                    "error": f"Unexpected error: {e}",
                    "location": f"Move {move_number}",
                    "time": time.strftime('%Y-%m-%d %H:%M:%S')
                })
                save_logs_on_exit()
                raise
        
        # Game over - determine result
        game.display_board()
        
        # Calculate game length
        game_length = move_number - 1
        
        if game.forfeit:
            winner = agent_black if game.forfeit == agent_white else agent_white
            loser = game.forfeit
            result = f"🏆 {winner.name} WINS! {loser.name} forfeited by exceeding the 10-second move limit."
            print(f"\n{result}")
            game_logs.append({"result": result})
            
            # Update agent values based on result
            winner.update_values("win", loser.name, game_length)
            loser.update_values("loss", winner.name, game_length)
            
        elif game.board.is_checkmate():
            winner = "White" if game.board.turn == chess.BLACK else "Black"
            winner_agent = agent_white if winner == "White" else agent_black
            loser_agent = agent_black if winner == "White" else agent_white
            result = f"🏆 {winner_agent.name} WINS by checkmate!"
            print(f"\n{result}")
            game_logs.append({"result": result})
            
            # Update agent values based on result
            winner_agent.update_values("win", loser_agent.name, game_length)
            loser_agent.update_values("loss", winner_agent.name, game_length)
            
        elif game.board.is_stalemate():
            result = "🤝 Stalemate! It's a draw."
            print(f"\n{result}")
            game_logs.append({"result": result})
            
            # Update agent values based on result
            agent_white.update_values("draw", agent_black.name, game_length)
            agent_black.update_values("draw", agent_white.name, game_length)
            
        else:
            result = "Game over!"
            print(f"\n{result}")
            game_logs.append({"result": result})
            
            # Update agent values based on result
            agent_white.update_values("draw", agent_black.name, game_length)
            agent_black.update_values("draw", agent_white.name, game_length)
        
        # Human feedback system
        print("\n" + "="*60)
        print("🎯 HUMAN FEEDBACK SYSTEM")
        print("="*60)
        print("Please rate each agent's performance in this game.")
        print("Rate from 1-10 where 10 is excellent and 1 is poor.")
        print()
        
        # Get feedback for White agent
        print(f"📊 Rating {agent_white.name} ({agent_white.personality}):")
        try:
            white_strategy = int(input("Strategy rating (1-10): "))
            if not 1 <= white_strategy <= 10:
                white_strategy = 5
                print("Invalid rating, using 5 as default.")
        except (ValueError, KeyboardInterrupt):
            white_strategy = 5
            print("Invalid input, using 5 as default.")
        
        try:
            white_personality = int(input("Personality rating (1-10): "))
            if not 1 <= white_personality <= 10:
                white_personality = 5
                print("Invalid rating, using 5 as default.")
        except (ValueError, KeyboardInterrupt):
            white_personality = 5
            print("Invalid input, using 5 as default.")
        
        white_comments = input("Additional feedback (optional): ").strip()
        if not white_comments:
            white_comments = None
        
        print()
        
        # Get feedback for Black agent
        print(f"📊 Rating {agent_black.name} ({agent_black.personality}):")
        try:
            black_strategy = int(input("Strategy rating (1-10): "))
            if not 1 <= black_strategy <= 10:
                black_strategy = 5
                print("Invalid rating, using 5 as default.")
        except (ValueError, KeyboardInterrupt):
            black_strategy = 5
            print("Invalid input, using 5 as default.")
        
        try:
            black_personality = int(input("Personality rating (1-10): "))
            if not 1 <= black_personality <= 10:
                black_personality = 5
                print("Invalid rating, using 5 as default.")
        except (ValueError, KeyboardInterrupt):
            black_personality = 5
            print("Invalid input, using 5 as default.")
        
        black_comments = input("Additional feedback (optional): ").strip()
        if not black_comments:
            black_comments = None
        
        print("\n🧠 Processing feedback with AI interpretation...")
        
        # Get AI interpretations
        white_interpretation = agent_white.interpret_human_feedback(white_strategy, white_personality, white_comments)
        black_interpretation = agent_black.interpret_human_feedback(black_strategy, black_personality, black_comments)
        
        print(f"\n💭 {agent_white.name}'s interpretation: {white_interpretation}")
        print(f"💭 {agent_black.name}'s interpretation: {black_interpretation}")
        
        # Add feedback to game logs
        game_logs.append({
            "type": "human_feedback",
            "white_strategy": white_strategy,
            "white_personality": white_personality,
            "white_comments": white_comments,
            "white_interpretation": white_interpretation,
            "black_strategy": black_strategy,
            "black_personality": black_personality,
            "black_comments": black_comments,
            "black_interpretation": black_interpretation
        })
        
        # Save agent memories
        print("\n💾 Saving agent memories...")
        agent_white.save_memory()
        agent_black.save_memory()
        
        # Generate philosophical reflections
        print("\n🧠 Generating philosophical reflections...")
        try:
            final_board_fen = game.board.fen()
            
            # Determine game result for each agent
            if game.forfeit:
                white_result = "win" if game.forfeit == agent_black else "loss"
                black_result = "win" if game.forfeit == agent_white else "loss"
            elif game.board.is_checkmate():
                winner = "White" if game.board.turn == chess.BLACK else "Black"
                white_result = "win" if winner == "White" else "loss"
                black_result = "win" if winner == "Black" else "loss"
            else:  # draw or other
                white_result = "draw"
                black_result = "draw"
            
            # Generate reflections
            white_reflection = agent_white.generate_philosophical_reflection(
                white_result, agent_black.name, game_length, final_board_fen
            )
            print(f"💭 {agent_white.name}'s Final Reflection: {white_reflection}")
            
            black_reflection = agent_black.generate_philosophical_reflection(
                black_result, agent_white.name, game_length, final_board_fen
            )
            print(f"💭 {agent_black.name}'s Final Reflection: {black_reflection}")
            
            # Add reflections to game logs
            game_logs.append({
                "type": "final_reflections",
                "white_reflection": white_reflection,
                "black_reflection": black_reflection,
                "game_length": game_length,
                "final_board": final_board_fen
            })
            
            # Evolve personalities based on reflections
            print("\n🔄 Evaluating personality evolution...")
            try:
                white_evolved = agent_white.evolve_personality(
                    white_result, agent_black.name, game_length, white_reflection
                )
                black_evolved = agent_black.evolve_personality(
                    black_result, agent_white.name, game_length, black_reflection
                )
                
                # Add personality evolution to game logs
                if white_evolved or black_evolved:
                    game_logs.append({
                        "type": "personality_evolution",
                        "white_evolved": white_evolved,
                        "black_evolved": black_evolved,
                        "white_personality": agent_white.personality,
                        "black_personality": agent_black.personality
                    })
                    
                    # Update current game state with new personalities
                    current_game_state['agent_white'] = f"{agent_white.name} ({agent_white.personality})"
                    current_game_state['agent_black'] = f"{agent_black.name} ({agent_black.personality})"
                
            except Exception as e:
                print(f"⚠️ Warning: Personality evolution evaluation failed: {e}")
            
        except Exception as e:
            print(f"⚠️ Warning: Philosophical reflection generation failed: {e}")
            game_logs.append({
                "type": "final_reflections",
                "error": f"Reflection generation failed: {e}"
            })
        
        # Save logs
        save_logs_on_exit()
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        game_logs.append({
            "error": f"Critical error: {e}",
            "location": "Main program",
            "time": time.strftime('%Y-%m-%d %H:%M:%S')
        })
        save_logs_on_exit()
        raise 