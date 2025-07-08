# AI Chess Agents Log Viewer

A beautiful web interface for viewing and analyzing AI chess agent game logs.

## Features

- 📊 **Agent Statistics**: View personality, win count, emotions, and move counts
- 🎨 **Color-coded Emotions**: Visual representation of agent feelings throughout the game
- 💬 **Interactive Dialogue**: See all agent conversations, questions, and answers
- 🧠 **Philosophical Reflections**: Read the agents' deep insights after each game
- 🔄 **Personality Evolution**: Track how agents' personalities change over time
- 📈 **Agent Values**: View the strategic values that influence agent behavior
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have some chess game log files in the current directory (files starting with `agent_chess_log_`)

## Usage

1. Start the web server:

```bash
python chess_log_viewer.py
```

2. Open your web browser and go to:

```
http://localhost:5000
```

3. Browse through your game logs and click on any game to view the detailed analysis.

## Features Explained

### Game List Page

- Shows all available game logs with key information
- Displays game mode (Rivalry/Collaborative)
- Shows final results and move counts
- Color-coded badges for quick identification

### Game Detail Page

#### Agent Statistics

- **Personality**: Current personality trait of each agent
- **Moves**: Number of moves made by each agent
- **Result**: Win/Loss/Draw status with color coding
- **Emotions**: Breakdown of all emotions felt during the game

#### Game Moves Table

- **Move Number**: Chronological order of moves
- **Agent**: Which agent made the move and their personality
- **Move**: The actual chess move with reasoning
- **Emotion**: Color-coded emotion badge for each move
- **Time**: How long the agent took to make the move
- **Subgoal**: The agent's current strategic objective
- **Dialogue & Reflections**: All conversations and thoughts

#### Color Coding

- **Green (Success)**: Confident, determined emotions
- **Blue (Info)**: Focused, playful emotions
- **Yellow (Warning)**: Excited, nervous emotions
- **Red (Danger)**: Worried emotions
- **Purple (Primary)**: Determined emotions

#### Special Sections

- **Final Philosophical Reflections**: Deep insights from both agents
- **Personality Evolution**: Any personality changes that occurred
- **Agent Values**: Strategic values that influenced behavior
- **Errors**: Any issues that occurred during the game

## File Structure

```
chess_game/
├── chess_log_viewer.py      # Main Flask application
├── templates/               # HTML templates
│   ├── base.html           # Base template with styling
│   ├── index.html          # Game list page
│   └── game.html           # Game detail page
├── requirements.txt         # Python dependencies
├── README_web_viewer.md    # This file
└── agent_chess_log_*.txt   # Game log files
```

## API Endpoints

- `GET /` - Main page with game list
- `GET /game/<filename>` - View specific game details
- `GET /api/games` - JSON API for game list

## Customization

### Adding New Emotions

To add new emotion colors, modify the `get_emotion_color()` function in `chess_log_viewer.py`:

```python
def get_emotion_color(feeling):
    emotion_colors = {
        'confident': 'success',
        'excited': 'warning',
        'focused': 'info',
        'determined': 'primary',
        'nervous': 'warning',
        'worried': 'danger',
        'playful': 'info',
        'your_new_emotion': 'your_color'  # Add new emotions here
    }
    return emotion_colors.get(feeling.lower(), 'secondary')
```

### Styling

The web interface uses Bootstrap 5 for styling. You can customize the appearance by modifying the CSS in `templates/base.html`.

## Troubleshooting

### No Game Logs Found

- Make sure you have run the AI chess agents at least once
- Check that log files start with `agent_chess_log_`
- Verify the log files are in the same directory as the Flask app

### Parsing Errors

- The viewer is designed to handle the specific format of AI chess agent logs
- If you see parsing errors, check that the log files are complete and not corrupted

### Port Already in Use

If port 5000 is already in use, modify the port in `chess_log_viewer.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Change port here
```

## Contributing

Feel free to enhance the viewer with additional features:

- Add chess board visualization
- Include move analysis
- Add export functionality
- Implement search and filtering
- Add game comparison tools

## License

This project is part of the AI Chess Agents system and follows the same license terms.
