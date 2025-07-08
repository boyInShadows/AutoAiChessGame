import os
import sys
import time

class ChessGame:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = 'white'
        self.game_over = False
        self.move_count = 0
        
    def initialize_board(self):
        """Initialize the chess board with pieces in starting positions"""
        board = [[' ' for _ in range(8)] for _ in range(8)]
        
        # Set up pawns
        for col in range(8):
            board[1][col] = '♟'  # Black pawns
            board[6][col] = '♙'  # White pawns
        
        # Set up other pieces
        black_pieces = ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜']
        white_pieces = ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']
        
        for col in range(8):
            board[0][col] = black_pieces[col]  # Black pieces
            board[7][col] = white_pieces[col]  # White pieces
            
        return board
    
    def display_board(self):
        """Display the current state of the board with improved UI"""
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
        
        # Header
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    SIMPLE CHESS GAME                        ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        
        # Game info
        print(f"  Move: {self.move_count:2d}  |  Current Player: {self.current_player.upper():5s}  |  Status: {'GAME OVER' if self.game_over else 'ACTIVE'}")
        print()
        
        # Board with improved styling
        print("        a     b     c     d     e     f     g     h")
        print("    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐")
        
        for row in range(8):
            print(f"  {8-row} │", end=" ")
            for col in range(8):
                piece = self.board[row][col]
                if piece == ' ':
                    # Better alternating colors for empty squares
                    if (row + col) % 2 == 0:
                        print("  □  │", end="")
                    else:
                        print("  ■  │", end="")
                else:
                    # Add spacing around pieces for better readability
                    print(f" {piece} │", end="")
            print(f" {8-row}")
            
            # Add horizontal lines between rows (except after last row)
            if row < 7:
                print("    ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤")
        
        print("    └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘")
        print("        a     b     c     d     e     f     g     h")
        print()
        
        # Legend
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │  PIECES: ♔♚=King  ♕♛=Queen  ♖♜=Rook  ♗♝=Bishop  ♘♞=Knight  ♙♟=Pawn  │")
        print("  └─────────────────────────────────────────────────────────────┘")
        print()
        
        # Instructions
        if not self.game_over:
            print("  📝 INSTRUCTIONS:")
            print("     • Enter moves as 'e2e4' (from square to square)")
            print("     • Type 'help' for move examples")
            print("     • Type 'quit' to exit game")
            print("     • Type 'board' to redisplay board")
            print()
    
    def show_help(self):
        """Display help information"""
        print("\n" + "="*60)
        print("  🎯 CHESS MOVE EXAMPLES:")
        print("  " + "="*60)
        print("  • e2e4    - Move pawn from e2 to e4")
        print("  • g1f3    - Move knight from g1 to f3")
        print("  • e1e2    - Move king from e1 to e2")
        print("  • a2a4    - Move pawn from a2 to a4")
        print("  • d1d8    - Move queen from d1 to d8")
        print()
        print("  📋 BOARD COORDINATES:")
        print("     Columns: a, b, c, d, e, f, g, h (left to right)")
        print("     Rows:    1, 2, 3, 4, 5, 6, 7, 8 (bottom to top)")
        print("     Example: e4 = column e, row 4")
        print("  " + "="*60)
        input("  Press Enter to continue...")
    
    def parse_move(self, move_str):
        """Parse move string like 'e2e4' into coordinates"""
        if len(move_str) != 4:
            return None, None
        
        try:
            from_col = ord(move_str[0].lower()) - ord('a')
            from_row = 8 - int(move_str[1])
            to_col = ord(move_str[2].lower()) - ord('a')
            to_row = 8 - int(move_str[3])
            
            if (0 <= from_row <= 7 and 0 <= from_col <= 7 and 
                0 <= to_row <= 7 and 0 <= to_col <= 7):
                return (from_row, from_col), (to_row, to_col)
        except:
            pass
        
        return None, None
    
    def is_valid_move(self, from_pos, to_pos):
        """Basic move validation"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Check if source position has a piece
        piece = self.board[from_row][from_col]
        if piece == ' ':
            return False, "No piece at source position"
        
        # Check if destination has own piece
        target_piece = self.board[to_row][to_col]
        if target_piece != ' ':
            # Check if it's the same color (uppercase = white, lowercase = black)
            if (piece.isupper() and target_piece.isupper()) or (piece.islower() and target_piece.islower()):
                return False, "Cannot capture your own piece"
        
        # Basic pawn movement (simplified)
        if piece in ['♙', '♟']:  # Pawns
            direction = -1 if piece == '♙' else 1  # White moves up, black moves down
            
            # Forward move
            if from_col == to_col and to_row == from_row + direction and target_piece == ' ':
                return True, ""
            
            # Capture move
            if abs(from_col - to_col) == 1 and to_row == from_row + direction and target_piece != ' ':
                return True, ""
        
        # Basic rook movement (simplified)
        elif piece in ['♖', '♜']:
            if from_row == to_row or from_col == to_col:
                # Check if path is clear (simplified - just check if destination is empty or enemy)
                return True, ""
        
        # Basic knight movement
        elif piece in ['♘', '♞']:
            row_diff = abs(from_row - to_row)
            col_diff = abs(from_col - to_col)
            if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
                return True, ""
        
        # Basic bishop movement (simplified)
        elif piece in ['♗', '♝']:
            if abs(from_row - to_row) == abs(from_col - to_col):
                return True, ""
        
        # Basic queen movement (simplified)
        elif piece in ['♕', '♛']:
            if (from_row == to_row or from_col == to_col or 
                abs(from_row - to_row) == abs(from_col - to_col)):
                return True, ""
        
        # Basic king movement
        elif piece in ['♔', '♚']:
            if abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1:
                return True, ""
        
        return False, "Invalid move for this piece"
    
    def make_move(self, from_pos, to_pos):
        """Execute a move on the board"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Move the piece
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = ' '
        
        # Switch players and increment move count
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        self.move_count += 1
    
    def show_game_over_screen(self, winner):
        """Display game over screen"""
        print("\n" + "="*60)
        print(f"  🏆 GAME OVER! {winner.upper()} WINS! 🏆")
        print("  " + "="*60)
        print(f"  Total moves played: {self.move_count}")
        print("  Thanks for playing Simple Chess!")
        print("  " + "="*60)
    
    def play(self):
        """Main game loop with improved UI"""
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    WELCOME TO CHESS!                        ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        print("  🎮 A simple chess game for two players")
        print("  📖 Type 'help' anytime for move examples")
        print()
        input("  Press Enter to start the game...")
        
        while not self.game_over:
            self.display_board()
            
            # Get move from player
            move_str = input(f"  {self.current_player.upper()}'s move (e.g., e2e4): ").strip().lower()
            
            if move_str == 'quit':
                print("\n  👋 Thanks for playing!")
                break
            elif move_str == 'help':
                self.show_help()
                continue
            elif move_str == 'board':
                continue  # Just redisplay the board
            
            # Parse move
            from_pos, to_pos = self.parse_move(move_str)
            if from_pos is None:
                print("  ❌ Invalid move format. Use format like 'e2e4'")
                print("  💡 Type 'help' for examples")
                input("  Press Enter to continue...")
                continue
            
            # Validate move
            is_valid, error_msg = self.is_valid_move(from_pos, to_pos)
            if not is_valid:
                print(f"  ❌ Invalid move: {error_msg}")
                input("  Press Enter to continue...")
                continue
            
            # Make move
            self.make_move(from_pos, to_pos)
            
            # Check for game over conditions (simplified)
            if self.current_player == 'white':
                # Check if black king is captured
                king_found = False
                for row in range(8):
                    for col in range(8):
                        if self.board[row][col] == '♚':
                            king_found = True
                            break
                    if king_found:
                        break
                
                if not king_found:
                    self.game_over = True
                    self.show_game_over_screen("WHITE")
            
            elif self.current_player == 'black':
                # Check if white king is captured
                king_found = False
                for row in range(8):
                    for col in range(8):
                        if self.board[row][col] == '♔':
                            king_found = True
                            break
                    if king_found:
                        break
                
                if not king_found:
                    self.game_over = True
                    self.show_game_over_screen("BLACK")
        
        if self.game_over:
            self.display_board()

def main():
    game = ChessGame()
    game.play()

if __name__ == "__main__":
    main() 