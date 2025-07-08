# AI Chess Agents with Personalities & Memory

An advanced chess system featuring AI agents with distinct personalities, emotions, memory, strategic dialogue, and philosophical reflections. Watch as AI agents evolve their playing styles and beliefs through gameplay experience.

## 🧠 Project Overview

This project implements sophisticated AI chess agents that go far beyond simple move calculation. Each agent has:

- **Unique personalities** (aggressive, defensive, analytical, etc.)
- **Emotional states** that change during gameplay
- **Long-term memory** of past games and experiences
- **Strategic dialogue** with opponents
- **Philosophical reflections** after each game
- **Personality evolution** based on experience
- **Value-based decision making** influenced by past results

## ✨ Key Features

### 🤖 AI Agent System

- **Personality-driven behavior**: Agents have distinct personalities that influence their playing style
- **Emotional states**: Agents experience feelings like confidence, nervousness, excitement, focus, etc.
- **Memory system**: Persistent memory of past games, moves, and experiences stored in JSON files
- **Value evolution**: Agent values (aggression, risk tolerance, patience, creativity, adaptability) change based on game outcomes
- **Strategic subgoals**: Dynamic goal-setting that adapts to the current board position

### 🎮 Game Modes

- **Rivalry Mode**: Agents compete aggressively, taunt each other, and try to mislead opponents
- **Collaborative Mode**: Agents give helpful advice, encouragement, and constructive feedback

### 💬 Interactive Dialogue

- **Strategic questions**: Agents ask tactical questions to their opponents
- **Characterful responses**: Answers reflect the agent's personality and current game mode
- **Move commentary**: Agents comment on their moves and feelings
- **Reflections**: Agents reflect on their current state and strategy

### 🧠 Advanced AI Features

- **Philosophical reflections**: Deep introspective analysis after each game
- **Core belief evolution**: Agents develop and modify their fundamental beliefs about chess and strategy
- **Personality evolution**: Subtle personality shifts based on experience and reflection
- **Value-based move selection**: Moves influenced by learned preferences and past success

### 📊 Web-Based Log Viewer

- **Beautiful web interface** built with Flask and Bootstrap
- **SVG board visualization**: Real-time board images for each move
- **Color-coded emotions**: Visual representation of agent emotional states
- **Game statistics**: Comprehensive stats and analysis
- **Move-by-move replay**: Detailed view of each move with dialogue and reflections
- **Agent evolution tracking**: History of personality and value changes

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key (for AI dialogue and reflections)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd chess_game
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Running the Game

1. **Start a chess game:**

   ```bash
   python ai_chess_agents.py
   ```

2. **Choose game mode:**

   - **Rivalry Mode**: Competitive gameplay with taunting and deception
   - **Collaborative Mode**: Supportive gameplay with advice and encouragement

3. **Watch the agents play:**
   - Each agent has 10 seconds per move
   - Observe their dialogue, questions, and reflections
   - See how their emotions and strategies evolve

### Viewing Game Logs

1. **Start the web viewer:**

   ```bash
   python chess_log_viewer.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Browse games:**
   - View list of all played games
   - Click on any game to see detailed analysis
   - Explore SVG board images for each move
   - Review agent statistics and evolution

## 🎯 Agent Personalities

### Available Personalities

- **Aggressive**: Prefers attacking moves and quick victories
- **Defensive**: Focuses on solid positions and safety
- **Analytical**: Methodical, calculating approach
- **Opportunistic**: Seeks tactical advantages
- **Cautious**: Risk-averse, patient play
- **Methodical**: Systematic, planned approach
- **Strategic**: Long-term planning focus
- **Dynamic**: Adaptable, flexible style
- **Bold**: Confident, daring moves
- **Creative**: Unconventional strategies
- **Patient**: Slow, methodical development
- **Assertive**: Confident, direct play

### Personality Evolution

Agents can evolve their personalities based on:

- Game results (wins, losses, draws)
- Playing style effectiveness
- Philosophical reflections
- Long-term experience patterns

## 📊 Agent Values System

Each agent maintains five core values that influence their behavior:

1. **Aggression Level** (0.0-1.0): Preference for attacking vs. defensive play
2. **Risk Tolerance** (0.0-1.0): Willingness to make risky moves
3. **Patience** (0.0-1.0): Preference for slow vs. fast play
4. **Creativity** (0.0-1.0): Tendency toward unconventional moves
5. **Adaptability** (0.0-1.0): Ability to adjust strategy

Values change based on:

- Game outcomes
- Move effectiveness
- Opponent behavior
- Game length and complexity

## 🧠 Memory & Learning

### Persistent Memory

- **Move history**: Every move with context and reasoning
- **Game results**: Outcomes against different opponents
- **Value evolution**: How values changed over time
- **Personality changes**: Evolution of personality traits
- **Core beliefs**: Fundamental beliefs about chess and strategy

### Learning Mechanisms

- **Value updates**: Values adjust based on game results
- **Belief formation**: New insights become core beliefs
- **Strategy refinement**: Successful patterns are reinforced
- **Personality adaptation**: Subtle shifts based on experience

## 🎮 Game Features

### Move Selection

- **Value-influenced**: Moves chosen based on current values
- **Personality-driven**: Style reflects agent personality
- **Memory-aware**: Considers past successful patterns
- **Subgoal-oriented**: Moves align with current strategic goals

### Strategic Dialogue

- **Contextual questions**: Based on current board position
- **Personality expression**: Dialogue reflects agent character
- **Mode-appropriate**: Different styles for rivalry vs. collaboration
- **Strategic depth**: Questions about tactics and plans

### Philosophical Reflections

- **Game analysis**: Deep thinking about the game experience
- **Self-awareness**: Insights about own playing style
- **Belief evolution**: Development of new perspectives
- **Strategic insights**: Learning from the game

## 📈 Web Viewer Features

### Game List

- **Chronological listing** of all games
- **Game metadata**: Date, agents, mode, result
- **Quick access** to detailed views

### Detailed Game View

- **SVG board images** for each move
- **Move-by-move analysis** with dialogue
- **Agent statistics** and emotion tracking
- **Final reflections** and personality evolution
- **Color-coded emotions** and game modes

### Interactive Elements

- **Hover effects** on board images
- **Responsive design** for different screen sizes
- **Professional styling** with Bootstrap
- **Easy navigation** between games

## 🛠️ Technical Architecture

### Core Components

- **Agent Class**: Personality, memory, and behavior management
- **ChessGame Class**: Game logic and SVG generation
- **Flask Web Server**: Log viewing and analysis interface
- **Memory System**: JSON-based persistent storage
- **SVG Generation**: Real-time board visualization

### File Structure

```
chess_game/
├── ai_chess_agents.py      # Main game logic
├── chess_log_viewer.py     # Web viewer server
├── simple_chess.py         # Basic chess implementation
├── requirements.txt        # Python dependencies
├── templates/              # Web templates
│   ├── base.html
│   ├── index.html
│   └── game.html
├── board_images/           # Generated SVG board images
├── memory_*.json           # Agent memory files
└── agent_chess_log_*.txt   # Game log files
```

## 🎯 Use Cases

### Research & Education

- **AI behavior study**: Observe how agents learn and evolve
- **Chess strategy analysis**: Study different playing styles
- **Personality modeling**: Understand AI personality development
- **Educational tool**: Learn chess through AI interaction

### Entertainment

- **Spectator sport**: Watch AI agents compete and interact
- **Interactive storytelling**: Follow agent development over time
- **Strategic discussion**: Engage with AI strategic thinking

### Development

- **AI behavior testing**: Experiment with different personality types
- **Memory system research**: Study long-term AI learning
- **Dialogue system development**: Explore AI communication patterns

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for AI dialogue and reflections
- `API_KEY`: Alternative name for OpenAI API key

### Customization Options

- **Personality types**: Add new personality definitions
- **Value ranges**: Adjust value update mechanisms
- **Memory limits**: Control memory file sizes
- **Game parameters**: Modify time limits and rules

## 🚀 Future Enhancements

### Planned Features

- **Multi-agent tournaments**: Multiple agents competing
- **Advanced personality types**: More sophisticated behavior models
- **Visual personality indicators**: UI elements showing personality traits
- **Real-time web interface**: Live game viewing
- **Agent training modes**: Customizable learning parameters

### Potential Improvements

- **Enhanced move analysis**: Deeper strategic evaluation
- **Social dynamics**: Agent relationships and alliances
- **Tournament systems**: Organized competition structures
- **Performance analytics**: Detailed statistical analysis

## 🤝 Contributing

This project welcomes contributions! Areas for improvement:

- New personality types
- Enhanced dialogue systems
- Improved web interface
- Additional analysis tools
- Performance optimizations

## 📄 License

This project is open source and available under the MIT License.

---

**Experience the future of AI chess - where every game tells a story of personality, learning, and evolution!** 🧠♟️✨
