import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QPushButton, QLabel, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt

class TicTacToeButton(QPushButton):
    def __init__(self, x, y):   
        super().__init__()
        self.x, self.y = x, y
        self.setText("") # Store button coordinates
        self.setFixedSize(100,100) # Set button size

class TicTacToeGame(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent # Reference to TournamentManager
        self.init_game()

    def init_game(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]  # Empty 3x3 board
        self.layout = QGridLayout()  # Grid layout for buttons
        self.buttons = {}
        for x in range(3):
            for y in range(3):
                button = TicTacToeButton(x, y)
                button.clicked.connect(self.make_move)  # Connect button to move function
                self.buttons[(x, y)] = button
                self.layout.addWidget(button, x, y)  # Add button to grid layout
        self.setLayout(self.layout)

    def make_move(self):
        if not self.parent.current_match or not self.parent.current_player:
            return  # If no active match or player, do nothing

        button = self.sender()
        if button.text() == "":
            current_symbol = self.parent.player_symbols[self.parent.current_player]
            button.setText(current_symbol)  # Mark the button with current player's symbol
            self.board[button.x][button.y] = current_symbol  # Update board

            winner = self.check_winner()
            if winner:  # Handle win or draw
                self.parent.round_complete(winner)
            else:
                self.parent.switch_player()  # Switch turns

    def check_winner(self):
        # Check rows, columns, diagonals for a winner or draw
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != '':
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != '':
                return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]
        if all(self.board[i][j] != '' for i in range(3) for j in range(3)):
            return 'Draw'  # If all cells are filled, it's a draw
        return None

    def reset_game(self):
        # Reset board and buttons for a new game
        self.board = [['' for _ in range(3)] for _ in range(3)]
        for button in self.buttons.values():
            button.setText("")

class TournamentManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic-Tac-Toe Tournament")
        self.setMinimumSize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.game_widget = TicTacToeGame(parent=self)  # Game widget
        self.setup_ui()
        self.reset_tournament_data()

    def reset_tournament_data(self):
        # Initialize tournament data
        self.players = []
        self.matches = []
        self.current_match = None
        self.current_player = None
        self.player_symbols = {}
        self.round_scores = {}
        self.points_table = {}
        self.current_round = 0
        self.tournament_stage = "setup"  # Start in setup stage

    def setup_ui(self):
        # Left side - Game and controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Player setup
        player_setup = QWidget()
        player_layout = QGridLayout(player_setup)
        self.player_inputs = []
        for i in range(4):  # Limiting to 4 players for simplicity
            label = QLabel(f"Player {i+1}:")
            input_field = QLineEdit()
            self.player_inputs.append(input_field)
            player_layout.addWidget(label, i, 0)
            player_layout.addWidget(input_field, i, 1)
        
        start_button = QPushButton("Start Tournament")
        start_button.clicked.connect(self.start_tournament)
        reset_button = QPushButton("Reset Tournament")
        reset_button.clicked.connect(self.reset_tournament)
        
        left_layout.addWidget(player_setup)
        left_layout.addWidget(self.game_widget)
        left_layout.addWidget(start_button)
        left_layout.addWidget(reset_button)
        
        # Right side - Tournament info
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.status_label = QLabel("Tournament Status: Setup")
        self.current_match_label = QLabel("Current Match: None")
        self.current_round_label = QLabel("Current Round: 0/5")
        self.round_score_label = QLabel("Round Scores: None")
        
        self.points_table_widget = QTableWidget()
        self.points_table_widget.setColumnCount(2)
        self.points_table_widget.setHorizontalHeaderLabels(["Player", "Points"])
        
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.current_match_label)
        right_layout.addWidget(self.current_round_label)
        right_layout.addWidget(self.round_score_label)
        right_layout.addWidget(self.points_table_widget)
        
        self.main_layout.addWidget(left_widget)
        self.main_layout.addWidget(right_widget)

    def start_tournament(self):  # Start the tournament with player names
        self.players = [input_field.text() for input_field in self.player_inputs if input_field.text()]
        if len(self.players) < 2:
            QMessageBox.warning(self, "Not Enough Players", "Please enter at least 2 player names.")
            return
        
        self.tournament_stage = "round-robin"  # Tournament starts
        self.matches = [(p1, p2) for i, p1 in enumerate(self.players) 
                        for p2 in self.players[i+1:]]
        self.points_table = {player: 0 for player in self.players}
        self.start_next_match()
        self.update_ui()

    def start_next_match(self):
        if not self.matches:
            self.end_tournament() # If no matches left, end tournament
            return
        
        self.current_match = self.matches.pop(0) # Get next match
        self.round_scores = {player: 0 for player in self.current_match}
        self.current_round = 0
        self.start_next_round()
        
    def start_next_round(self):
        self.current_round += 1
        self.game_widget.reset_game() # Start new round
        self.player_symbols = {
            self.current_match[0]: 'X',
            self.current_match[1]: 'O'
        }
        self.current_player = self.current_match[0]
        self.update_ui()

    def switch_player(self):  # Switch between the two players
        self.current_player = self.current_match[1] if self.current_player == self.current_match[0] else self.current_match[0]
        self.update_ui()

    def round_complete(self, result):
        if result == 'Draw':
            QMessageBox.information(self, "Round Complete", "This round is a draw!")
        else:
            winner = None
            for player, symbol in self.player_symbols.items():
                if symbol == result:
                    winner = player
                    break
            
            if winner is not None:
                self.round_scores[winner] += 1
                QMessageBox.information(self, "Round Complete", f"{winner} wins this round!")
        
        if self.current_round < 5:
            self.start_next_round()
        else:
            self.end_match()

    def end_match(self):
        match_winner = max(self.round_scores.items(), key=lambda x: x[1])[0]
        self.points_table[match_winner] += 5  # Add points to the match winner
        QMessageBox.information(self, "Match Complete", 
                               f"Match Winner: {match_winner}\nScores: {self.round_scores}")
        self.start_next_match()

    def end_tournament(self):
        winner = max(self.points_table.items(), key=lambda x: x[1])[0]
        QMessageBox.information(self, "Tournament Ended", f"Tournament Winner: {winner}")
        self.tournament_stage = "complete"
        self.current_match = None
        self.update_ui()

    def reset_tournament(self):
        self.reset_tournament_data()
        self.game_widget.reset_game() # Reset the game and UI for a new tournament
        for input_field in self.player_inputs:
            input_field.clear()
        self.update_ui()

    def update_ui(self): # Update UI elements based on current match, round, and player status
        self.status_label.setText(f"Tournament Status: {self.tournament_stage.capitalize()}")
        
        if self.current_match:
            self.current_match_label.setText(f"Current Match: {self.current_match[0]} vs {self.current_match[1]}")
            self.current_round_label.setText(f"Current Round: {self.current_round}/5")
            if self.current_player:
                current_symbol = self.player_symbols[self.current_player]
                self.status_label.setText(f"Current Player: {self.current_player} ({current_symbol})")
        else:
            self.current_match_label.setText("Current Match: None")
            self.current_round_label.setText("Current Round: 0/5")
        
        round_scores_text = "Round Scores: "
        if self.round_scores:
            round_scores_text += ", ".join([f"{player}: {score}" for player, score in self.round_scores.items()])
        self.round_score_label.setText(round_scores_text)
        
        self.points_table_widget.setRowCount(len(self.points_table))
        for row, (player, points) in enumerate(self.points_table.items()):
            self.points_table_widget.setItem(row, 0, QTableWidgetItem(player))
            self.points_table_widget.setItem(row, 1, QTableWidgetItem(str(points)))

if __name__ == '__main__':  
    app = QApplication(sys.argv)
    tournament = TournamentManager()
    tournament.show()
    sys.exit(app.exec_())