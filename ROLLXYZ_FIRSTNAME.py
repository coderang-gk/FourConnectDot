#!/usr/bin/env python3
from FourConnect import * # See the FourConnect.py file
import csv


def get_valid_actions_ordered(state):
    center_column = len(state[0]) // 2
    actions = [(abs(center_column - col), col) for col in range(len(state[0])) if state[0][col] == 0]
    actions.sort()  # Sort by distance from the center
    return [action[1] for action in actions]  # Return only the column indices


class GameTreePlayer:

    def __init__(self,fourConnect):
        self.fourConnect = fourConnect

        pass

    def FindBestAction(self, currentState):
        alpha = float('-inf')  # Initialize alpha
        beta = float('inf')  # Initialize beta
        return self.minimax(currentState, 6, True, alpha, beta , self.fourConnect)[1]

    def minimax(self, state, depth, isMaximizingPlayer, alpha, beta, fourConnect):
        if depth == 0 or game_over(state, fourConnect):
            return [evaluate(state), None]
        valid_actions = get_valid_actions_ordered(state)
        if isMaximizingPlayer:
            maxEval = float('-inf')
            bestAction = None
            for action in get_valid_actions(state):
                new_state = simulate_action(state, action, 2)  # 2 is the GameTree player
                eval = self.minimax(new_state, depth - 1, False, alpha, beta, fourConnect)[0]
                if eval > maxEval:
                    maxEval = eval
                    bestAction = action
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return [maxEval, bestAction]
        else:
            minEval = float('inf')
            bestAction = None
            for action in get_valid_actions(state):
                new_state = simulate_action(state, action, 1)  # 1 is the Myopic player
                eval = self.minimax(new_state, depth - 1, True, alpha, beta, fourConnect)[0]
                if eval < minEval:
                    minEval = eval
                    bestAction = action
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return [minEval, bestAction]


def game_over(state,fourConnect):
    # Implement logic to check if the game is over
    # Check for a win or if all cells are filled
    return fourConnect.winner is not None or all_cells_filled(state)

def all_cells_filled(state):
    return all(all(col != 0 for col in row) for row in state)

def evaluate(state):
    # Implement an evaluation function
    # For example, count the number of 2s (GameTreePlayer) in a row, column, or diagonal
    # More sophisticated evaluations can consider blocking the opponent, creating multiple threats, etc.
    # Return a numerical score
    return some_evaluation_score(state)

def get_valid_actions(state):
    # Return a list of column indices where a coin can be placed
    # Special check for first and last columns to ensure they have enough space for a vertical Connect Four
    valid_actions = []
    for col in range(len(state[0])):
        if (col == 0 or col == len(state[0]) - 1) and not column_has_space_for_vertical(state, col):
            continue  # Skip this column if it's the first or last and doesn't have space for a vertical Connect Four
        if state[0][col] == 0:
            valid_actions.append(col)
    return valid_actions

def column_has_space_for_vertical(state, col):
    # Check if there are at least 4 empty spaces in the column for a vertical Connect Four
    return sum(1 for row in state if row[col] == 0) >= 4


def check_urgent_block(state, row_idx, col_idx, token, urgent_block_multiplier):
    """
    Specifically check for patterns like 1,1,0,1 and apply a high score for blocking these.
    """
    score = 0

    # Check horizontal, vertical, and two diagonal directions
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for delta_row, delta_col in directions:
        score += urgent_block_score(state, row_idx, col_idx, delta_row, delta_col, token, urgent_block_multiplier)

    return score

def urgent_block_score(state, row_idx, col_idx, delta_row, delta_col, token, urgent_block_multiplier):
    """
    Check for a specific urgent block pattern in a given direction.
    """
    pattern_score = 0
    try:
        if (state[row_idx][col_idx] == token and
            state[row_idx + delta_row][col_idx + delta_col] == token and
            state[row_idx + 2 * delta_row][col_idx + 2 * delta_col] == 0 and
            state[row_idx + 3 * delta_row][col_idx + 3 * delta_col] == token):
                pattern_score = urgent_block_multiplier
    except IndexError:
        # Out of bounds - ignore
        pass

    return pattern_score


def simulate_action(state, action, player):
    # Simulate dropping a coin into the chosen column
    # Return the new state without altering the original state
    new_state = copy.deepcopy(state)
    for row in reversed(new_state):
        if row[action] == 0:
            row[action] = player
            break
    return new_state

# Add your implementation for some_evaluation_score
def some_evaluation_score(state):
    player_token = 2  # Assuming 2 is the AI's token
    opponent_token = 1  # Assuming 1 is the opponent's token
    score = 0

    # Function to count sequences of a given length for a specific token
    def count_sequences(token, length):
        count = 0
        # Check horizontal sequences
        for row in state:
            for col in range(len(row) - length + 1):
                if all(row[col + i] == token for i in range(length)):
                    count += 1

        # Check vertical sequences
        for col in range(len(state[0])):
            for row in range(len(state) - length + 1):
                if all(state[row + i][col] == token for i in range(length)):
                    count += 1

        # Check diagonal sequences (down-right and down-left)
        for row in range(len(state) - length + 1):
            for col in range(len(state[0]) - length + 1):
                if all(state[row + i][col + i] == token for i in range(length)):
                    count += 1
                if all(state[row + i][col - i] == token for i in range(length)):
                    count += 1

        return count

    # Scoring based on sequences of 2, 3, and 4
    score += count_sequences(player_token, 4) * 100
    score += count_sequences(player_token, 3) * 10
    score -= count_sequences(opponent_token, 4) * 100
    score -= count_sequences(opponent_token, 3) * 10

    return score

def LoadTestcaseStateFromCSVfile():
    testcaseState=list()

    with open('testcase.csv', 'r') as read_obj: 
        csvReader = csv.reader(read_obj)
        for csvRow in csvReader:
            row = [int(r) for r in csvRow]
            testcaseState.append(row)
        return testcaseState


def PlayGame():
    fourConnect = FourConnect()
    fourConnect.PrintGameState()
    gameTree = GameTreePlayer(fourConnect)

    move = 0
    while move < 42:  # At most 42 moves are possible
        if move % 2 == 0:  # Myopic player always moves first
            fourConnect.MyopicPlayerAction()
        else:
            currentState = fourConnect.GetCurrentState()
            gameTreeAction = gameTree.FindBestAction(currentState)
            fourConnect.GameTreePlayerAction(gameTreeAction)
        fourConnect.PrintGameState()
        move += 1
        if fourConnect.winner != None:
            break

    return fourConnect.winner, move


def RunMultipleGames(num_games=10):
    player2_wins = 0
    total_moves = 0

    for _ in range(num_games):
        winner, moves = PlayGame()
        if winner == 2:
            player2_wins += 1
            total_moves += moves

    print(f"Player 2 won {player2_wins} out of {num_games} games.")
    if player2_wins > 0:
        print(f"Average number of moves for Player 2 to win: {total_moves / player2_wins:.2f}")
    else:
        print("Player 2 did not win any games.")

def RunTestCase():
    """
    This procedure reads the state in testcase.csv file and start the game.
    Player 2 moves first. Player 2 must win in 5 moves to pass the testcase; Otherwise, the program fails to pass the testcase.
    """
    
    fourConnect = FourConnect()
    gameTree = GameTreePlayer(fourConnect)
    testcaseState = LoadTestcaseStateFromCSVfile()
    fourConnect.SetCurrentState(testcaseState)
    fourConnect.PrintGameState()

    move=0
    while move<5: #Player 2 must win in 5 moves
        if move%2 == 1: 
            fourConnect.MyopicPlayerAction()
        else:
            currentState = fourConnect.GetCurrentState()
            gameTreeAction = gameTree.FindBestAction(currentState)
            fourConnect.GameTreePlayerAction(gameTreeAction)
        fourConnect.PrintGameState()
        move += 1
        if fourConnect.winner!=None:
            break
    
    print("Roll no : 2020B3A71470G") #Put your roll number here
    
    if fourConnect.winner==2:
        print("Player 2 has won. Testcase passed.")
    else:
        print("Player 2 could not win in 5 moves. Testcase failed.")
    print("Moves : {0}".format(move))
    

def main():
    fourConnect = FourConnect()
    gameTree = GameTreePlayer(fourConnect)
    RunMultipleGames()
    """
    You can modify PlayGame function for writing the report
    Modify the FindBestAction in GameTreePlayer class to implement Game tree search.
    You can add functions to GameTreePlayer class as required.
    """

    """
        The above code (PlayGame()) must be COMMENTED while submitting this program.
        The below code (RunTestCase()) must be UNCOMMENTED while submitting this program.
        Output should be your rollnumber and the bestAction.
        See the code for RunTestCase() to understand what is expected.
    """
    
    #RunTestCase()


if __name__=='__main__':
    main()
