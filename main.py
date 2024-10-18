import tkinter as tk
from tkinter import messagebox
import random
import copy

# Constants for the game
ROWS = 6
COLUMNS = 7
EMPTY = 0
YELLOW = 1
RED = 2

# Create the game window
window = tk.Tk()
window.withdraw()  # Hide the game window until difficulty is selected
window.title("Siris's Connect 4")

# Game board as a 2D array (6 rows, 7 columns)
board = [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]

# Track whose turn it is (1 for yellow, 2 for red)
current_player = random.choice([YELLOW, RED])  # Flip a coin to decide who starts

# Difficulty level: "beginner", "medium", or "hard"
difficulty = ""

# Button references and canvas references
buttons = []
canvases = []


def check_for_winner(current_board, player):
    """Checks the board for a winner (4 in a row, vertically, horizontally, or diagonally)."""
    # Check horizontal
    for row in range(ROWS):
        for col in range(COLUMNS - 3):
            if current_board[row][col] == player and all(current_board[row][col + i] == player for i in range(4)):
                return True

    # Check vertical
    for row in range(ROWS - 3):
        for col in range(COLUMNS):
            if current_board[row][col] == player and all(current_board[row + i][col] == player for i in range(4)):
                return True

    # Check diagonal (top-left to bottom-right)
    for row in range(ROWS - 3):
        for col in range(COLUMNS - 3):
            if current_board[row][col] == player and all(current_board[row + i][col + i] == player for i in range(4)):
                return True

    # Check diagonal (bottom-left to top-right)
    for row in range(3, ROWS):
        for col in range(COLUMNS - 3):
            if current_board[row][col] == player and all(current_board[row - i][col + i] == player for i in range(4)):
                return True

    return False


def is_board_full(current_board):
    """Checks if the board is completely full."""
    return all(current_board[0][col] != EMPTY for col in range(COLUMNS))


def drop_piece_on_board(board, row, col, player):
    """Places the player's piece in the given row and column."""
    board[row][col] = player


def find_valid_moves(current_board):
    """Returns a list of valid columns where a piece can be dropped."""
    return [col for col in range(COLUMNS) if current_board[0][col] == EMPTY]


def get_next_open_row(current_board, col):
    """Finds the next available row in the selected column."""
    for row in range(ROWS - 1, -1, -1):
        if current_board[row][col] == EMPTY:
            return row
    return None


def minimax(current_board, depth, alpha, beta, maximizing_player):
    """Minimax algorithm with alpha-beta pruning for the Hard AI."""
    valid_moves = find_valid_moves(current_board)
    is_terminal = check_for_winner(current_board, YELLOW) or check_for_winner(current_board, RED) or is_board_full(
        current_board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if check_for_winner(current_board, RED):  # AI wins
                return (None, 1000000000)
            elif check_for_winner(current_board, YELLOW):  # Player wins
                return (None, -1000000000)
            else:  # Tie
                return (None, 0)
        else:  # Depth is zero, no more lookahead
            return (None, score_position(current_board, RED))

    if maximizing_player:  # AI's move (Red)
        value = -float('inf')
        best_column = random.choice(valid_moves)
        for col in valid_moves:
            row = get_next_open_row(current_board, col)
            temp_board = copy.deepcopy(current_board)
            drop_piece_on_board(temp_board, row, col, RED)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_column, value

    else:  # Player's move (Yellow)
        value = float('inf')
        best_column = random.choice(valid_moves)
        for col in valid_moves:
            row = get_next_open_row(current_board, col)
            temp_board = copy.deepcopy(current_board)
            drop_piece_on_board(temp_board, row, col, YELLOW)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_column, value


def score_position(current_board, player):
    """Scores the current board position for the AI."""
    score = 0

    # Score horizontal
    for row in range(ROWS):
        row_array = [current_board[row][col] for col in range(COLUMNS)]
        for col in range(COLUMNS - 3):
            window = row_array[col:col + 4]
            score += evaluate_window(window, player)

    # Score vertical
    for col in range(COLUMNS):
        col_array = [current_board[row][col] for row in range(ROWS)]
        for row in range(ROWS - 3):
            window = col_array[row:row + 4]
            score += evaluate_window(window, player)

    # Score positive sloped diagonals
    for row in range(ROWS - 3):
        for col in range(COLUMNS - 3):
            window = [current_board[row + i][col + i] for i in range(4)]
            score += evaluate_window(window, player)

    # Score negative sloped diagonals
    for row in range(3, ROWS):
        for col in range(COLUMNS - 3):
            window = [current_board[row - i][col + i] for i in range(4)]
            score += evaluate_window(window, player)

    return score


def evaluate_window(window, player):
    """Evaluates a 4-cell window and assigns a score."""
    score = 0
    opponent = YELLOW if player == RED else RED

    if window.count(player) == 4:
        score += 100
    elif window.count(player) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(player) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def ai_move_hard():
    """Hard AI that uses minimax to make a move."""
    column, minimax_score = minimax(board, 2, -float('inf'), float('inf'), True)
    drop_piece(column)


def drop_piece(column):
    """Handles the logic for dropping a piece into the selected column."""
    global current_player

    # Find the lowest empty spot in the column
    row = get_next_open_row(board, column)
    if row is not None:
        board[row][column] = current_player

        # Update the canvas to show the circular chip
        canvases[row][column].create_oval(5, 5, 75, 75, fill='yellow' if current_player == YELLOW else 'red')

        # Check if this move resulted in a win
        if check_for_winner(board, current_player):
            winner = "Yellow" if current_player == YELLOW else "Red"
            messagebox.showinfo("Game Over", f"{winner} wins!")
            reset_game()
        else:
            # Switch to the other player
            current_player = RED if current_player == YELLOW else YELLOW
            if current_player == RED and difficulty == "hard":
                window.after(500, ai_move_hard)  # Let AI take its turn after a short delay
            elif current_player == RED:
                window.after(500, ai_move)  # Let AI take its turn after a short delay
    else:
        messagebox.showwarning("Column Full", "This column is full! Choose another one.")


def ai_move():
    """Medium and Beginner AI."""
    available_columns = [col for col in range(COLUMNS) if board[0][col] == EMPTY]
    if available_columns:
        drop_piece(random.choice(available_columns))


def reset_game():
    """Resets the game board to start a new game."""
    global board, current_player
    board = [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]
    current_player = random.choice([YELLOW, RED])  # Flip a coin again for a new game

    # Reset the canvases to white (empty)
    for row in canvases:
        for canvas in row:
            canvas.delete("all")

    # If the AI starts first, let it move
    if current_player == RED:
        if difficulty == "hard":
            window.after(500, ai_move_hard)
        else:
            window.after(500, ai_move)


def select_difficulty(selected_difficulty):
    """Sets the difficulty based on the button clicked."""
    global difficulty
    difficulty = selected_difficulty
    difficulty_window.destroy()  # Close the difficulty selection window
    window.deiconify()  # Show the game window after difficulty is selected


def ask_for_difficulty():
    """Prompts the user to choose a difficulty level using clickable buttons."""
    global difficulty_window
    difficulty_window = tk.Toplevel(window)
    difficulty_window.title("Select Difficulty")

    # Create Beginner, Medium, and Hard buttons
    beginner_button = tk.Button(difficulty_window, text="Beginner", width=20, height=2,
                                command=lambda: select_difficulty("beginner"))
    beginner_button.pack(padx=20, pady=10)

    medium_button = tk.Button(difficulty_window, text="Medium", width=20, height=2,
                              command=lambda: select_difficulty("medium"))
    medium_button.pack(padx=20, pady=10)

    hard_button = tk.Button(difficulty_window, text="Hard", width=20, height=2,
                            command=lambda: select_difficulty("hard"))
    hard_button.pack(padx=20, pady=10)


def create_board():
    """Creates the GUI board with clickable buttons and canvases for circular chips."""
    for row in range(ROWS):
        button_row = []
        canvas_row = []
        for col in range(COLUMNS):
            frame = tk.Frame(window, width=80, height=80, bg='blue')
            frame.grid(row=row, column=col, padx=5, pady=5)

            # Create a canvas to simulate the circular chips
            canvas = tk.Canvas(frame, width=80, height=80, bg='white')
            canvas.pack()

            # Make the canvas clickable for human player moves
            canvas.bind("<Button-1>", lambda event, col=col: drop_piece(col))

            button_row.append(frame)
            canvas_row.append(canvas)

        buttons.append(button_row)
        canvases.append(canvas_row)


# Ask the user for the difficulty before starting the game
ask_for_difficulty()

# Wait for the difficulty window to close, then create the game board
window.wait_window(difficulty_window)
create_board()

# If the AI goes first, let it make the first move
if current_player == RED:
    if difficulty == "hard":
        window.after(500, ai_move_hard)
    else:
        window.after(500, ai_move)

# Run the Tkinter event loop
window.mainloop()
