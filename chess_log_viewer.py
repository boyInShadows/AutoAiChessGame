from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import re
import json
from datetime import datetime
import glob

app = Flask(__name__)

def parse_game_log(log_file_path):
    """Parse a chess game log file and extract structured data"""
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract game metadata
        game_data = {
            'filename': os.path.basename(log_file_path),
            'date': None,
            'white_agent': None,
            'black_agent': None,
            'game_mode': None,
            'white_values': None,
            'black_values': None,
            'moves': [],
            'final_result': None,
            'final_reflections': None,
            'personality_evolution': None,
            'human_feedback': None,
            'errors': []
        }
        
        lines = content.split('\n')
        
        # Parse header information
        for line in lines:
            if line.startswith('Date:'):
                game_data['date'] = line.replace('Date:', '').strip()
            elif line.startswith('White:'):
                game_data['white_agent'] = line.replace('White:', '').strip()
            elif line.startswith('Black:'):
                game_data['black_agent'] = line.replace('Black:', '').strip()
            elif line.startswith('Mode:'):
                game_data['game_mode'] = line.replace('Mode:', '').strip()
            elif line.startswith('  White Values:'):
                game_data['white_values'] = line.replace('  White Values:', '').strip()
            elif line.startswith('  Black Values:'):
                game_data['black_values'] = line.replace('  Black Values:', '').strip()
            elif line.startswith('🏁 FINAL RESULT:'):
                game_data['final_result'] = line.replace('🏁 FINAL RESULT:', '').strip()
            elif line.startswith('🧠 FINAL PHILOSOPHICAL REFLECTIONS:'):
                # Parse final reflections
                reflection_lines = []
                i = lines.index(line) + 1
                while i < len(lines) and not lines[i].startswith('='):
                    if lines[i].strip() and not lines[i].startswith('   Game Length:'):
                        reflection_lines.append(lines[i].strip())
                    i += 1
                game_data['final_reflections'] = '\n'.join(reflection_lines)
            elif line.startswith('🔄 PERSONALITY EVOLUTION:'):
                # Parse personality evolution
                evolution_lines = []
                i = lines.index(line) + 1
                while i < len(lines) and not lines[i].startswith('='):
                    if lines[i].strip():
                        evolution_lines.append(lines[i].strip())
                    i += 1
                game_data['personality_evolution'] = '\n'.join(evolution_lines)
            elif line.startswith('🎯 HUMAN FEEDBACK:'):
                # Parse human feedback
                feedback_lines = []
                i = lines.index(line) + 1
                while i < len(lines) and not lines[i].startswith('='):
                    if lines[i].strip():
                        feedback_lines.append(lines[i].strip())
                    i += 1
                game_data['human_feedback'] = '\n'.join(feedback_lines)
            elif line.startswith('❌ ERROR:'):
                game_data['errors'].append(line.strip())
        
        # Parse moves
        move_fields = {
            'Move': 'move',
            'Reasoning': 'reasoning',
            'Time taken': 'time_taken',
            'Feeling': 'feeling',
            'Subgoal': 'subgoal',
            'Dialogue': 'dialogue',
            'Question': 'question',
            'Answer': 'answer',
            'Reflection': 'reflection',
            'Mode': 'game_mode',
            'Board Image': 'svg_file',
        }
        current_move = None
        for line in lines:
            if re.match(r'Move \d+ - .+:', line):
                # Start of a new move
                if current_move:
                    game_data['moves'].append(current_move)
                
                # Extract move information
                move_match = re.match(r'Move (\d+) - (.+?) \((.+?)\):', line)
                if move_match:
                    current_move = {
                        'move_number': int(move_match.group(1)),
                        'agent_name': move_match.group(2),
                        'personality': move_match.group(3),
                        'move': None,
                        'reasoning': None,
                        'time_taken': None,
                        'feeling': None,
                        'subgoal': None,
                        'dialogue': None,
                        'question': None,
                        'answer': None,
                        'reflection': None,
                        'game_mode': None,
                        'svg_file': None
                    }
            elif current_move:
                label, separator, value = line.strip().partition(':')
                if separator and label in move_fields:
                    current_move[move_fields[label]] = value.strip()
        
        # Add the last move
        if current_move:
            game_data['moves'].append(current_move)
        
        return game_data
        
    except Exception as e:
        return {
            'filename': os.path.basename(log_file_path),
            'error': f'Failed to parse log file: {str(e)}'
        }

def get_emotion_color(feeling):
    """Return CSS color class based on feeling"""
    emotion_colors = {
        'confident': 'success',
        'excited': 'warning',
        'focused': 'info',
        'determined': 'primary',
        'nervous': 'warning',
        'worried': 'danger',
        'playful': 'info'
    }
    return emotion_colors.get(feeling.lower(), 'secondary')

def get_agent_stats(game_data):
    """Calculate agent statistics from game data"""
    if not game_data.get('moves'):
        return {}
    
    stats = {
        'white': {'name': game_data.get('white_agent', 'Unknown'), 'moves': 0, 'feelings': {}, 'personality': None},
        'black': {'name': game_data.get('black_agent', 'Unknown'), 'moves': 0, 'feelings': {}, 'personality': None}
    }
    
    for move in game_data['moves']:
        agent_name = move['agent_name']
        if 'white' in agent_name.lower() or game_data.get('white_agent', '').split(' ')[0] in agent_name:
            stats['white']['moves'] += 1
            stats['white']['personality'] = move['personality']
            if move['feeling']:
                stats['white']['feelings'][move['feeling']] = stats['white']['feelings'].get(move['feeling'], 0) + 1
        else:
            stats['black']['moves'] += 1
            stats['black']['personality'] = move['personality']
            if move['feeling']:
                stats['black']['feelings'][move['feeling']] = stats['black']['feelings'].get(move['feeling'], 0) + 1
    
    # Determine winner
    if game_data.get('final_result'):
        if 'white' in game_data['final_result'].lower() or 'alpha' in game_data['final_result'].lower():
            stats['white']['result'] = 'win'
            stats['black']['result'] = 'loss'
        elif 'black' in game_data['final_result'].lower() or 'beta' in game_data['final_result'].lower():
            stats['white']['result'] = 'loss'
            stats['black']['result'] = 'win'
        else:
            stats['white']['result'] = 'draw'
            stats['black']['result'] = 'draw'
    
    return stats

@app.route('/')
def index():
    """Main page showing list of available game logs"""
    log_files = glob.glob('agent_chess_log_*.txt')
    games = []
    
    for log_file in sorted(log_files, reverse=True):
        game_data = parse_game_log(log_file)
        if 'error' not in game_data:
            games.append(game_data)
    
    return render_template('index.html', games=games)

@app.route('/game/<filename>')
def view_game(filename):
    """View a specific game log"""
    log_file_path = filename
    if not os.path.exists(log_file_path):
        return "Game log not found", 404
    
    game_data = parse_game_log(log_file_path)
    if 'error' in game_data:
        return f"Error parsing game log: {game_data['error']}", 500
    
    agent_stats = get_agent_stats(game_data)
    
    return render_template('game.html', 
                         game=game_data, 
                         stats=agent_stats,
                         get_emotion_color=get_emotion_color)

@app.route('/api/games')
def api_games():
    """API endpoint to get list of games"""
    log_files = glob.glob('agent_chess_log_*.txt')
    games = []
    
    for log_file in sorted(log_files, reverse=True):
        game_data = parse_game_log(log_file)
        if 'error' not in game_data:
            games.append({
                'filename': game_data['filename'],
                'date': game_data['date'],
                'white_agent': game_data['white_agent'],
                'black_agent': game_data['black_agent'],
                'game_mode': game_data['game_mode'],
                'final_result': game_data['final_result']
            })
    
    return jsonify(games)

@app.route('/board_images/<path:filename>')
def serve_svg(filename):
    """Serve SVG board images"""
    return send_from_directory('board_images', filename, mimetype='image/svg+xml')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
