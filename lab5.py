#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""


# NO IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    '''
    board = []
    mask = []
    for i in range(num_rows):
        #initialize board with correct size and filled with 0s
        board.append([0]*num_cols)
        mask.append([False]*num_cols)

    
    
    for bomb in bombs:
        m,n = bomb
        board[m][n] = '.'
        for i in range(-1,2): # -1 to 1
            for j in range(-1,2): # -1 to 1
                # iterates over all 8 squares around the bomb
                x = m + i
                y = n + j
                if x in range(0,num_rows) and y in range(0,num_cols) and board[x][y] != '.': 
                    # if x and y are valid board positions and are not currently bombs, increment by 1
                    board[x][y] += 1
    return {
        'dimensions': (num_rows, num_cols),
        'board' : board,
        'mask' : mask,
        'state': 'ongoing'}
    '''
    return new_game_nd((num_rows,num_cols),bombs) # used nd implementation


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """

    return dig_nd(game, (row,col)) # use nd implementation

    """
        def check_victory():
            check if we have won
            
            board = game['board']
            mask = game['mask']
            m,n = game['dimensions']

            victory = True
            for i in range(m):
                for j in range(n):
                if board[i][j] != '.' and not mask[i][j]:
                    victory = False
            
            if victory:
                game['state'] = 'victory'

        m,n = game['dimensions']
        board = game['board']

        assert row in range(0,m) and col in range(0,n) # ensure that we are digging up a valid square

        if game['state'] == 'defeat' or game['state'] == 'victory': # nothing to do if we have already won
            return 0 # revealed no squares
        
        if board[row][col] == '.': # if we dig up a bomb, then we lose
            game['mask'][row][col] = True
            game['state'] = 'defeat'
            return 1 # revealed one square

        elif board[row][col] == 0 and not game['mask'][row][col]: # if we have not already dug this square and that it corresponds to a 0
            revealed = 1
            game['mask'][row][col] = True
            for i in range(-1,2):
                for j in range(-1,2):
                    x = row + i
                    y = col + j
                    if x in range(0,m) and y in range(0,n):
                        revealed += dig_2d(game,x,y)
                        check_victory()
            return revealed

        elif not game['mask'][row][col]: # if we have not dug this square and it does not correspond to a 0 or a bomb
            game['mask'][row][col] = True
            check_victory()
            return 1
        
        else: # if we have already dug this square, do nothing (prevent infinite recursion)
            return 0
    """

    '''
        if game['state'] == 'defeat' or game['state'] == 'victory':
            game['state'] = game['state']  # keep the state the same
            return 0

        if game['board'][row][col] == '.':
            game['mask'][row][col] = True
            game['state'] = 'defeat'
            return 1

        bombs = 0
        covered_squares = 0
        for r in range(game['dimensions'][0]):
            for c in range(game['dimensions'][1]):
                if game['board'][r][c] == '.':
                    if  game['mask'][r][c] == True:
                        bombs += 1
                elif game['mask'][r][c] == False:
                    covered_squares += 1
        if bombs != 0:
            # if bombs is not equal to zero, set the game state to defeat and
            # return 0
            game['state'] = 'defeat'
            return 0
        if covered_squares == 0:
            game['state'] = 'victory'
            return 0

        if game['mask'][row][col] != True:
            game['mask'][row][col] = True
            revealed = 1
        else:
            return 0

        if game['board'][row][col] == 0:
            num_rows, num_cols = game['dimensions']
            if 0 <= row-1 < num_rows:
                if 0 <= col-1 < num_cols:
                    if game['board'][row-1][col-1] != '.':
                        if game['mask'][row-1][col-1] == False:
                            revealed += dig_2d(game, row-1, col-1)
            if 0 <= row < num_rows:
                if 0 <= col-1 < num_cols:
                    if game['board'][row][col-1] != '.':
                        if game['mask'][row][col-1] == False:
                            revealed += dig_2d(game, row, col-1)
            if 0 <= row+1 < num_rows:
                if 0 <= col-1 < num_cols:
                    if game['board'][row+1][col-1] != '.':
                        if game['mask'][row+1][col-1] == False:
                            revealed += dig_2d(game, row+1, col-1)
            if 0 <= row-1 < num_rows:
                if 0 <= col < num_cols:
                    if game['board'][row-1][col] != '.':
                        if game['mask'][row-1][col] == False:
                            revealed += dig_2d(game, row-1, col)
            if 0 <= row < num_rows:
                if 0 <= col < num_cols:
                    if game['board'][row][col] != '.':
                        if game['mask'][row][col] == False:
                            revealed += dig_2d(game, row, col)
            if 0 <= row+1 < num_rows:
                if 0 <= col < num_cols:
                    if game['board'][row+1][col] != '.':
                        if game['mask'][row+1][col] == False:
                            revealed += dig_2d(game, row+1, col)
            if 0 <= row-1 < num_rows:
                if 0 <= col+1 < num_cols:
                    if game['board'][row-1][col+1] != '.':
                        if game['mask'][row-1][col+1] == False:
                            revealed += dig_2d(game, row-1, col+1)
            if 0 <= row < num_rows:
                if 0 <= col+1 < num_cols:
                    if game['board'][row][col+1] != '.':
                        if game['mask'][row][col+1] == False:
                            revealed += dig_2d(game, row, col+1)
            if 0 <= row+1 < num_rows:
                if 0 <= col+1 < num_cols:
                    if game['board'][row+1][col+1] != '.':
                        if game['mask'][row+1][col+1] == False:
                            revealed += dig_2d(game, row+1, col+1)

        bombs = 0  # set number of bombs to 0
        covered_squares = 0
        for r in range(game['dimensions'][0]):
            # for each r,
            for c in range(game['dimensions'][1]):
                # for each c,
                if game['board'][r][c] == '.':
                    if  game['mask'][r][c] == True:
                        # if the game mask is True, and the board is '.', add 1 to
                        # bombs
                        bombs += 1
                elif game['mask'][r][c] == False:
                    covered_squares += 1
        bad_squares = bombs + covered_squares
        if bad_squares > 0:
            game['state'] = 'ongoing'
            return revealed
        else:
            game['state'] = 'victory'
            return revealed
    '''

def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    """
        elem_dict = {
            0: ' ',
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            '.': '.'
        }

        m,n = game['dimensions']

        board = game['board']

        mask = game['mask']

        rV = []

        for i in range(m):
            rV.append([])
            for j in range(n):
                if (xray or mask[i][j]):
                    elem = elem_dict[board[i][j]]
                else:
                    elem = '_'
                rV[-1].append(elem)
        
        return rV
    """
    return render_nd(game, xray) # use nd implementation

def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    rendered = render_2d(game, xray)

    rV = ''
    for i in range(len(rendered)):
        rV += ''.join(rendered[i])
        if i != len(rendered)-1:
            rV += '\n'
    
    return rV

# N-D IMPLEMENTATION

def list_builder(size,val): 
        """
        size: n-tuple, val: what the list will be filled with
        new method for building n-dimensional arrays because of issues with pointers
        """
        N = len(size)
        if N == 1:
            return [val] * size[0]
        else:
            rV = []
            for i in range(size[0]):
                rV.append(list_builder(size[1:],val))
            return rV

def neighbors(tup):
    """
    input is tuple of coordinates
    returns all neighbors of the tuple as a list of lists
    """
    first = tup[0]
    if len(tup) == 1:
        return [[first-1],[first],[first+1]]
    else:
        rV = []
        for i in range(-1,2):
            for elem in neighbors(tup[1:]):
                rV.append([first+i] + elem)
        return rV

def get_element(game, coordinates, key):
    """
    input:
    game: game dict, coordinates: tuple of coordinates, key: string that is a key to game dict, tells which value in dict to search in
    returns:
    the value at the location at game[key]
    """
    N = len(coordinates)
    def recurse(sub_obj,n):
            # replaces the element at the index with a bomb
            loc = coordinates[n]
            if n != N-1:
                return recurse(sub_obj[loc],n+1)
            else:
                return sub_obj[loc]
    return recurse(game[key],0)

def update_element(game,coordinates,key,val): 
    """
    game: game dict, coordinates: n-tuple, key: what to update in game, val: what to change to
    """
    N = len(coordinates)
    def recurse(sub_obj,n):
            # replaces the element at the index with a bomb
            loc = coordinates[n]
            if n != N-1:
                recurse(sub_obj[loc],n+1)
            else:
                sub_obj[loc] = val
    recurse(game[key], 0)

def all_coords(dim):
    """
    takes in the tuple of dimensions, returns a list of lists of all valid coordinates
    """
    size = dim[0]
    if len(dim) == 1:
        return [[i] for i in range(size)]
    else:
        rV = []
        for i in range(size):
            for elem in all_coords(dim[1:]):
                rV.append([i] + elem)
        return rV

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    coords = set()
    for elem in all_coords(dimensions):
        coords.add(tuple(elem))
    
    def bomb_update(b, bomb_loc):
        update_element(b, bomb_loc, 'board', '.')
        for neighbor in neighbors(bomb_loc):
            loc = tuple(neighbor)
            if loc in coords:
                entry = get_element(b,loc, 'board')
                if entry != '.':
                    update_element(b,loc, 'board', entry+1)
        #print(rV)
    
    board = {'board': list_builder(dimensions, 0)}
    mask = list_builder(dimensions, False)
    for bomb in bombs:
        bomb_update(board, bomb)
    
    return {
        'dimensions': dimensions,
        'board' : board['board'],
        'mask' : mask,
        'state': 'ongoing'}

def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
    coordinates (tuple): Where to start digging

    Returns:
    int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """

    dimensions = game['dimensions']

    if game['state'] == 'defeat' or game['state'] == 'victory': # nothing to do if we have already won or lost
        return 0 # revealed no squares

    # generate set of all valid coordinates
    coords = set() 
    for coord in all_coords(dimensions):
        coords.add(tuple(coord))

    def check_victory(): 
        """
        check if we have won
        """
        victory = True
        for loc in coords:
            if not get_element(game,loc,'mask') and get_element(game,loc,'board') != '.': # has not been revealed and is not bomb
                victory = False
        if victory:
            game['state'] = 'victory'
    
    assert coordinates in coords

    if get_element(game,coordinates, 'mask') == True: # already revealed, nothing to do
        return 0

    if get_element(game, coordinates, 'board') == '.': # bomb = u dead
        update_element(game,coordinates, 'mask', True)
        game['state'] = 'defeat'
        return 1
    
    #if 0, then we have to actually do stuff rip
    """
    if get_element(game,coordinates,'board') == 0:
        revealed = 1
        update_element(game,coordinates, 'mask', True)
        neighbor_list = neighbors(coordinates)
        for neighbor in neighbor_list:
            if tuple(neighbor) in coords:
                revealed += dig_nd(game,tuple(neighbor))
        check_victory()
        return revealed
    else:
            update_element(game,coordinates, 'mask', True)
            check_victory()
            return 1
    """
    def dig_recurse(game, loc, seen):
        if loc in seen:
            return 0
        if loc in coords and not get_element(game,loc,'mask'):
            seen.add(loc)
            update_element(game,loc, 'mask', True)
            if get_element(game,loc, 'board') == 0:
                revealed = 1
                for neighbor in neighbors(loc):
                    revealed += dig_recurse(game, tuple(neighbor), seen)
                return revealed
            else:
                return 1
        else:
            return 0

    if get_element(game,coordinates,'board') == 0:
        rV = dig_recurse(game, coordinates, set())
        check_victory()
        return rV
    else:
        update_element(game,coordinates,'mask', True)
        check_victory()
        return 1


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """

    
    dimensions = game['dimensions']

    rV = {'rV': list_builder(dimensions, '_')}

    coords = set()
    for coord in all_coords(dimensions):
        coords.add(tuple(coord))
    
    for coordinates in coords:
        if get_element(game,coordinates, 'mask') or xray:
            entry = get_element(game,coordinates, 'board')
            if entry == 0:
                entry = ' '
            update_element(rV, coordinates, 'rV', str(entry))
    
    return rV['rV']


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests
    
    """
    with open('test_inputs/testnd_integration1.pickle','rb') as f:
        inputs = pickle.load(f)
    print(inputs)

    g = new_game_nd(inputs['dimensions'], inputs['bombs'])
    print('new game')
    print(render_nd(g))

    for dig in inputs['digs']:
        print('digging', dig)
        dig_nd(g,dig)
    
    print(render_nd(g))
    """
    
    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    #
    #doctest.run_docstring_examples(render_2d, globals(), optionflags=_doctest_flags, verbose=False)
