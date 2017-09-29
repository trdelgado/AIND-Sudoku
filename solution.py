assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # keep a list of boxes with two digits
    pair_list = []

    # Loop through each unit of the puzzle
    for unit in unitlist:
        # Loop through each box
        for box in unit:
            # If box has two digits append to box pair list
            if len(values[box]) == 2:
                pair_list.append([box, values[box]])

        # If only two boxes and have same two digits
        if len(pair_list) == 2 and pair_list[0][1] == pair_list[1][1]:

            # Keep track of both boxes and digits
            first_digit = pair_list[0][1][0]
            second_digit = pair_list[0][1][1]
            first_box = pair_list[0][0]
            second_box = pair_list[1][0]

            # Eliminate both digits from all other boxes in same unit
            for box in unit:
                # If a peer has digit remove from peer since only the original box can have digit
                if box != first_box and box != second_box:
                    new_val = values[box].replace(first_digit,'')
                    values = assign_value(values, box, new_val)
                    new_val = values[box].replace(second_digit,'')
                    values = assign_value(values, box, new_val)

        # Reset pair list for next loop
        pair_list = []

    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """

    chars = []
    digits = '123456789'
    # Loop through each character in the grid string
    for c in grid:
        # Check and append chars
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)

    # Verify number if characters are valid
    assert len(chars) == 81

    # Return the sudoku dictionry 
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    # Keep a list of boxes that have a unique solution
    solved_values = [box for box in values.keys() if len(values[box]) == 1]

    # Loop through each solved box
    for box in solved_values:
        # Get the solved box's solution
        digit = values[box]

        # Loop through box's peers to see if they have the box's solution
        for peer in peers[box]:
            # If a peer has digit remove from peer since only the original box can have digit
            values[peer] = values[peer].replace(digit,'')

    # return update dictionary 
    return values

def only_choice(values):
    # Loop through each unit
    for unit in unitlist:

        # Loop through each digit 
        for digit in '123456789':
            # Keep a list of boxes that have the digit in its list of possible solutions
            dplaces = [box for box in unit if digit in values[box]]

            # If there is only one box with the digit it is the unique solution
            if len(dplaces) == 1:
                # Update the square to have just the single digit
                values = assign_value(values, dplaces[0], digit)

    return values

def reduce_puzzle(values):
    # List of squares solved with one value
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False

    # Keep reducing the puzzle solution until solution found or has stalled
    while not stalled:
        # Marker to see how many boxes were solved before reducing the puzzle
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        
        # Eliminate possible solutions from peer boxes if solution found for a single box
        values = eliminate(values)

        # Search each unit for boxes that have unique digits and assign box accordingly
        values = only_choice(values)

        # Marker to see how many boxes were solved after reducing the puzzle
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        # Check if puzzle got updated
        stalled = solved_values_before == solved_values_after

        # If the number of solved squares is the same as before, puzzle has stalled
        if len([box for box in values.keys() if len(values[box]) == 0]):

            # Eliminate values using the naked twins strategy (last resort since method is slower)
            values = naked_twins(values)

            # Update and check if the puzzle has still stalled
            solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
            stalled = solved_values_before == solved_values_after

            if len([box for box in values.keys() if len(values[box]) == 0]):
                return False

    # Return reduced puzzles solution
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    
    # Check if puzzle has stalled
    if values == False:
        return False
        
    # Check if puzzle has been solved with unique values for each square
    if all([len(values[box]) == 1 for box in boxes]):
        return values
        
    # Choose one of the unfilled squares with the fewest possibilities
    numbers, square = min([(values[box], box) for box in boxes if len(values[box]) > 1])

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for number in numbers:
        test_values = values.copy()
        test_values[square] = number
        attempt = search(test_values)
        
        # If attempt has a solution return dictionary
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Convert the string grid into a dictionary 
    board = grid_values(grid)

    # Search for a solution
    v = search(board)

    # If found returns a dictionary with solution else returns false
    if isinstance(v, dict):
        return v
    else:
        return False


rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diag_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'], ['I1', 'H2', 'G3', 'F4', 'E5', 'D6', 'C7', 'B8', 'A9']] # add diagnol units to check for
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

if __name__ == '__main__':
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    # Test cases
    diag_sudoku_grid_1 = '....1.8..8..6...5.45.9.3.7....3...9.9.7...4.3.3...1....1.8.4.65.4...6..1..6.7....'
    diag_sudoku_grid_2 = '...15...37.4...1.......276..7.9...2....8.6....9...5.4..352.......7...2.12...91...'
    diag_sudoku_grid_3 = '95......78..7..1.9..7...54..6.2....1...168...7....9.5..75...6..2.4..1..51......32'
    diag_sudoku_grid_4 = '...5..1.6.....749.7.5..9.3...2....4..362.195..5....6...8.1..3.4.634.....5.4..3...'
    diag_sudoku_grid_5 = '..8..9.3.3.....1.......2..7.89.24....1..5..4....18.92.2..7.......7.....9.6.4..3..'
    diag_sudoku_grid_6 = '8......7.965..7.....352......69487.............26734......615.....3..941.5......3'
    diag_sudoku_grid_7 = '........518..549.......124......918....4.3....638......716.......297..518........'
    diag_sudoku_grid_8 = '3.4..5....7...1.5.9.....4....97.8.25..7...8..18.5.29....6.....7.4.8...9....4..5.3'
    diag_sudoku_grid_9 = '.3........4..819..5..4...3...87.3....1..2..4....8.46...2...8..6..925..1........7.'
    diag_sudoku_grid_10 = '1..3......68..1.7.7..8..3....4..2..6....4....5..1..4....9..3..7.7.5..14......8..2'
    diag_sudoku_grid_11 = '.6...84...3..7.........3.85.....42.11.......37.29.....25.1.........8..1...87...5.'
    diag_sudoku_grid_12 = '.2...1..9.3....4..6.1.7.8.......6.3..5.2.8.1..1.5.......2.8.7.5..9....8.3..7...6.'
    diag_sudoku_grid_13 = '.....3......4.7....53...49..........53..1..42..........69...57....6.2......3.....'
    diag_sudoku_grid_14 = '...7.9....85...31.2......7...........1..7.6......8...7.7.........3......85.......'
    diag_sudoku_grid_15 = '.....9....85...31.2......7...........1....6......8...7.7.........3......85.......'

    display(solve(diag_sudoku_grid_15))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
