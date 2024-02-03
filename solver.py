class Solved(Exception):
    pass

def solve_bfs(level, steplimit):
    from collections import deque
    import time
    flag_positions = read_flags(level)
    state = read_state(level)
    moves_startpos = 5*(steplimit+1)

    start = time.time()
    visited = set()
    q = deque()
    q.append((state, 0))
    maxsteps = 0
    moves_to_check = allocate_possible_moves_array()

    while len(q) > 0:
        state, moves_steps_compressed = q.popleft()
        steps_compressed = moves_steps_compressed % moves_startpos
        moves = moves_steps_compressed // moves_startpos
        forbidden_move = steps_compressed % 5
        steps = steps_compressed // 5
        index = state % 70              # get_pawn_position(state) inlined
        x, y = index % 10, index // 10  #
        for i in moves_to_check[x][y][forbidden_move]:
            try:
                remaining_steps = steplimit - steps
                new_state, stepped, new_forbidden_move = move(state, x, y, i, flag_positions, remaining_steps)
                if new_state in visited:
                    continue
                if stepped:
                    new_steps = steps + 1
                    if new_steps > maxsteps:
                        maxsteps = new_steps
                        print("Checking", new_steps, "step solutions...", time.time() - start, "s elapsed")
                        print("Visited:", len(visited), " Queue size:", len(q))
                    # Flag too far:
                    flag_too_far = False
                    new_index = new_state % 70                      # get_pawn_position(state) inlined
                    new_x, new_y = new_index % 10, new_index // 10  #
                    for flagpos, flagno in flag_positions.items():
                        if not (new_state // FLAG_STARTPOS) & (1 << flagno): # flag_is_captured(new_state, flagno) inlined
                            flagx, flagy = flagpos % 10, flagpos // 10
                            if abs(flagx - new_x) + abs(flagy - new_y) > remaining_steps - 1:
                                flag_too_far = True
                                break
                    if flag_too_far:
                        continue
                else:
                    new_steps = steps
                q.append((new_state, (new_forbidden_move+1) + 5*new_steps + moves_startpos*(i + 4 * moves)))
                visited.add(new_state)
                #if len(visited) > 20000000:
                #    visited.pop()
            except Cant:
                continue
            except Solved:
                if steps + 1 > maxsteps:
                    print("Checking", steps + 1, "step solutions...", time.time() - start, "s elapsed")
                    print("Visited:", len(visited), " Queue size:", len(q))
                print(write_state(state, flag_positions))
                print("Solved in", time.time() - start, "s,", steps+1, "steps:", read_solution(level, i + 4 * moves))
                return
    print("No solution exists ( with steps <=", steplimit, "); the check took", time.time() - start, "s")

def solve_dfs(level, steplimit, movelimit=9999, accept_any=False):
    import time
    flag_positions = read_flags(level)
    state = read_state(level)

    start = time.time()
    visited = dict()
    moves_to_check = allocate_possible_moves_array()

    moves = 0
    steps = 0
    index = state % 70              # get_pawn_position(state) inlined
    x, y = index % 10, index // 10  #
    best = None
    for i in moves_to_check[x][y][0]:
        res = recursive_solve(state, i, steps, i + 4 * moves, 1, movelimit, steplimit, visited, flag_positions, moves_to_check, accept_any)
        if res:
            if accept_any:
                best = res
                break
            if not best or best[3] > res[3]:
                best = res
    if best:
        print(write_state(best[0], flag_positions))
        print("Solved in", time.time() - start, "s,", best[1], "steps:", read_solution(level, best[2]))
        return
    print("No solution exists ( with steps <=", steplimit, "); the check took", time.time() - start, "s")

def recursive_solve(state, i, steps, moves, moves_num, moves_left, steplimit, visited, flag_positions, moves_to_check, accept_any):
    try:
        index = state % 70              # get_pawn_position(state) inlined
        x, y = index % 10, index // 10  #
        remaining_steps = steplimit - steps
        new_state, stepped, new_forbidden_move = move(state, x, y, i, flag_positions, remaining_steps)

        if not stepped and moves_left == 0:
            return None

        if new_state in visited:
            if visited[new_state] < steps:
                return None
            if accept_any and visited[new_state] == steps:
                return None
            visited[new_state] = steps
        elif len(visited) < 50000000:
            visited[new_state] = steps

        if stepped:
            new_steps = steps + 1
            # Flag too far:
            flag_too_far = False
            new_index = new_state % 70                      # get_pawn_position(state) inlined
            new_x, new_y = new_index % 10, new_index // 10  #
            for flagpos, flagno in flag_positions.items():
                if not (new_state // FLAG_STARTPOS) & (1 << flagno): # flag_is_captured(new_state, flagno) inlined
                    flagx, flagy = flagpos % 10, flagpos // 10
                    if abs(flagx - new_x) + abs(flagy - new_y) > remaining_steps - 1:
                        flag_too_far = True
                        break
            if flag_too_far:
               return None
        else:
            new_steps = steps
            new_x, new_y = x, y

        best = None
        for j in moves_to_check[new_x][new_y][new_forbidden_move+1]:
            res = recursive_solve(new_state, j, new_steps, j + 4 * moves, moves_num+1, moves_left if stepped else moves_left - 1, steplimit, visited, flag_positions, moves_to_check, accept_any)
            if res:
                if accept_any:
                    return res
                if not best or best[3] > res[3]:
                    best = res
        if best:
            return best
        return None
    except Cant:
        return None
    except Solved:
        return state, steps + 1, moves, moves_num
    

def solve_dfs2(level, steplimit):
    import time
    flag_positions = read_flags(level)
    state = read_state(level)

    start = time.time()
    visited = dict()
    moves_to_check = allocate_possible_moves_array()

    moves = 0
    steps = 0
    index = state % 70              # get_pawn_position(state) inlined
    x, y = index % 10, index // 10  #
    for i in moves_to_check[x][y][0]:
        res = recursive_solve2(state, i, steps, i + 4 * moves, 1, steplimit, visited, flag_positions, moves_to_check)
        if res:
            state = read_state(level)
            solution = clean_solution(state, read_moves(res[2], res[3]), flag_positions, moves_to_check)
            steps = 0
            for i in range(len(solution)):
                x, y = get_pawn_position(state)
                try:
                    state, step, _ = move(state, x, y, solution[i], flag_positions, 9999)
                except Solved:
                    print(write_state(res[0], flag_positions))
                    print("Solved in", time.time() - start, "s,", steps, "steps:", solution)
                    return
                if step:
                    steps += 1
    print("No solution exists ( with steps <=", steplimit, "); the check took", time.time() - start, "s")

def recursive_solve2(state, i, steps, moves, moves_num, steplimit, visited, flag_positions, moves_to_check):
    try:
        index = state % 70              # get_pawn_position(state) inlined
        x, y = index % 10, index // 10  #
        remaining_steps = steplimit - steps
        new_state, stepped, new_forbidden_move = move(state, x, y, i, flag_positions, remaining_steps)

        if new_state in visited:
            if visited[new_state] <= steps:
                return None
            visited[new_state] = steps
        elif len(visited) < 50000000:
            visited[new_state] = steps

        if stepped:
            new_steps = steps + 1
            # Flag too far:
            flag_too_far = False
            new_index = new_state % 70                      # get_pawn_position(state) inlined
            new_x, new_y = new_index % 10, new_index // 10  #
            for flagpos, flagno in flag_positions.items():
                if not (new_state // FLAG_STARTPOS) & (1 << flagno): # flag_is_captured(new_state, flagno) inlined
                    flagx, flagy = flagpos % 10, flagpos // 10
                    if abs(flagx - new_x) + abs(flagy - new_y) > remaining_steps - 1:
                        flag_too_far = True
                        break
            if flag_too_far:
               return None
        else:
            new_steps = steps
            new_x, new_y = x, y

        for j in moves_to_check[new_x][new_y][new_forbidden_move+1]:
            res = recursive_solve2(new_state, j, new_steps, j + 4 * moves, moves_num+1, steplimit, visited, flag_positions, moves_to_check)
            if res:
                return res
        return None
    except Cant:
        return None
    except Solved:
        return state, steps + 1, moves, moves_num
    
def clean_solution(initial_state, solution, flag_positions, moves_to_check):
    was_step = []
    state = initial_state
    for i in range(len(solution)):
        x, y = get_pawn_position(state)
        try:
            state, step, _ = move(state, x, y, solution[i], flag_positions, 9999)
            was_step.append(step)
        except Solved:
            break
    
    return attempt_solution(initial_state, 0, solution, was_step, flag_positions, moves_to_check)

def attempt_solution(old_state, i, solution, was_step, flag_positions, moves_to_check):
    if i >= len(solution):
        return None
    x, y = get_pawn_position(old_state)
    try:
        new_state, step, forbidden_move = move(old_state, x, y, solution[i], flag_positions, 9999)
        if step != was_step[i]:
            return None

        new_x, new_y = get_pawn_position(new_state)
        if i < len(solution)-1 and solution[i+1] not in moves_to_check[new_x][new_y][forbidden_move+1]:
            return None
        
        if not step:
            # Try skipping this move
            res = attempt_solution(old_state, i+1, solution, was_step, flag_positions, moves_to_check)
            if res:
                return res
        
        # Just proceed
        res = attempt_solution(new_state, i+1, solution, was_step, flag_positions, moves_to_check)
        if res:
            return [solution[i]] + res
        return None
    except Cant:
        return None
    except Solved:
        return [solution[i]]
    
def read_solution(level, moves):
    # [X], [0, X], [0, 0, X] etc. all compress to the same moves value, brute-forcing the right one:
    candidate = read_moves(moves)
    moves_num = len(candidate)
    while not verify_solution(level, candidate):
        if moves_num > 1000:
            return None # Solution given is invalid
        moves_num += 1
        candidate = read_moves(moves, moves_num)
    return candidate

def read_moves(moves, moves_num=None):
    rest = moves
    l = []
    while rest > 0:
        move = rest % 4
        l.append(move)
        rest //= 4
    l.reverse()
    if moves_num == None:
        return l
    return [0]*(moves_num - len(l)) + l

def allocate_possible_moves_array():
    moves_to_check = [[0 for _ in range(7)] for _ in range(10)]
    for i in range(10):
        for j in range(7):
            if i == 0:
                moves_to_check[i][j] = [[0,1,3], [1,3], [0,3], [0,1,3], [0,1]]
            elif i == 9:
                moves_to_check[i][j] = [[1,2,3], [1,2,3], [2,3], [1,3], [1,2]]
            elif j == 0:
                moves_to_check[i][j] = [[0,2,3], [2,3], [0,2,3], [0,3], [0,2]]
            elif j == 6:
                moves_to_check[i][j] = [[0,1,2], [1,2], [0,2], [0,1], [0,1,2]]
            else:
                moves_to_check[i][j] = [[0,1,2,3], [1,2,3], [0,2,3], [0,1,3], [0,1,2]]
    moves_to_check[0][0] = [[0,3], [3], [0,3], [0,3], [0]]
    moves_to_check[0][6] = [[0,1], [1], [0], [0,1], [0,1]]
    moves_to_check[9][0] = [[2,3], [2,3], [2,3], [3], [2]]
    moves_to_check[9][6] = [[1,2], [1,2], [2], [1], [1,2]]
    return moves_to_check

def read_flags(level):
    flag_positions = dict()
    flagno = 0
    for i in range(0, len(level), 3):
        if level[i+1:i+2:] == 'P':
            flag_positions[i//3] = flagno
            flagno += 1
    return flag_positions

def read_pawn(level):
    for i in range(0, len(level), 3):
        if level[i+1:i+2:] == 'O':
            return i//3
    return None

def read_state(level):
    blocks = 0
    for i in range(0, len(level), 3):
        if level[i:i+3:] in ['[ ]', '[P]', '[O]']:
            blocks += 1 << (i//3)
    return read_pawn(level) + blocks*70

def write_state(state, flag_positions):
    pawn_x, pawn_y = get_pawn_position(state)
    level = ""
    for i in range(70):
        x = i % 10
        y = i // 10
        piece = ' '
        if i in flag_positions:
            if not flag_is_captured(state, flag_positions[i]):
                piece = 'P'
        if x == pawn_x and y == pawn_y:
            piece = 'O'
        if has_block(x, y, state):
            level += '[' + piece + ']'
        else:
            level += ' ' + piece + ' '
        if i % 10 == 9:
            level += '\n'
    return level

FLAG_STARTPOS = 70*(1 << 70)

def flag_is_captured(state, flag):
    return (state // FLAG_STARTPOS) & (1 << flag)

def has_block(x, y, state):
    return ((state // 70) % FLAG_STARTPOS) & (1 << (x + y*10))

def get_pawn_position(state):
    index = state % 70
    return index % 10, index // 10

def capture_flag(state, flag, flag_positions):
    new_state = state + FLAG_STARTPOS*(1 << flag)
    if new_state // FLAG_STARTPOS == (1 << len(flag_positions)) - 1:
        raise Solved
    return new_state

class Cant(Exception):
    pass

def move(state, x, y, code, flag_positions, remaining_steps):
    blockstate = (state // 70) % FLAG_STARTPOS
    horizontal_move = code == 0 or code == 2
    forbidden_move = -1
    next_x, next_y = (x + 1-code, y) if horizontal_move else (x, y + code-2)
    if blockstate & (1 << (next_x + next_y*10)): # has_block(next_x, next_y, state) inlined
        if remaining_steps <= 0:
            raise Cant
        # Take a step
        next_index = next_x + next_y*10
        if next_index in flag_positions and not flag_is_captured(state, flag_positions[next_index]):
            state = capture_flag(state, flag_positions[next_index], flag_positions)
        else:
            if blockstate & (1 << (x + y*10)): # has_block(x, y, state) inlined
                forbidden_move = (2 - code) if horizontal_move else (4 - code) # don't step back unless just captured a flag
        return state + (next_x-x) + (next_y-y)*10, True, forbidden_move
    elif blockstate & (1 << (x + y*10)): # has_block(x, y, state) inlined
            # Move block
            new_state = state - 70*(1 << (x + y*10))
            distance_moved = 0
            while True:
                x, y = next_x, next_y
                if (code == 0 and x == 9) or (code == 1 and y == 0) or (code == 2 and x == 0) or (code == 3 and y == 6):
                    break
                next_x, next_y = (x + 1-code, y) if horizontal_move else (x, y + code-2)
                if blockstate & (1 << (next_x + next_y*10)): # has_block(next_x, next_y, state) inlined
                    break
                forbidden_move = code # The moved block is out of reach in its direction
                distance_moved += 1
                if distance_moved >= remaining_steps - 2: # The moved block cant ever be reached
                    raise Cant
            return new_state + 70*(1 << (x + y*10)), False, forbidden_move
    raise Cant

def play(level, moves):
    import time
    flag_positions = read_flags(level)
    state = read_state(level)
    steps = 0
    time.sleep(1)
    for i in range(len(moves)):
        x, y = get_pawn_position(state)
        try:
            state, step, _ = move(state, x, y, moves[i], flag_positions, 9999)
        except Solved:
            return
        if step:
            steps += 1
        time.sleep(0.8)
        print("move n#", i+1, "step n#", steps)
        print(write_state(state, flag_positions))

def verify_solution(level, moves):
    flag_positions = read_flags(level)
    state = read_state(level)
    steps = 0
    try:
        for i in range(len(moves)):
            x, y = get_pawn_position(state)
            state, step, _ = move(state, x, y, moves[i], flag_positions, 9999)
            if step:
                steps += 1
    except Cant:
        return False
    except Solved:
        return True
    return False

if __name__ == "__main__":
    level1 = str(
                "   [ ][ ][ ]   [ ][ ][ ]   [ ]"
                "         [ ]                  "
                " P                         [ ]"
                "                           [ ]"
                "                        [ ]   "
                "                        [ ]   "
                "                     [P][ ][O]"
            ), 23
    level2 = str(
                "                              "
                "   [ ][ ][ ]      [ ][ ][ ]   "
                "   [ ]                  [ ]   "
                "             P  P             "
                "   [ ]                  [ ]   "
                "   [ ][ ][ ]      [ ][ ][O]   "
                "                              "
            ), 34
    level3 = str(
                " P [ ]               [ ]      "
                "               [ ][ ]   [ ][ ]"
                "                     [ ][ ]   "
                "[ ]   [ ]         [ ][ ]   [ ]"
                "            [ ][ ]            "
                "[ ]            [ ]   [ ][ ]   "
                "      [ ][ ][ ][ ]      [ ][O]"
            ), 19
    level = level1
    #play(level[0], [2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 0, 2, 3, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2])
    #solve_bfs(level[0], steplimit=level[1])
    solve_dfs(level[0], steplimit=level[1], movelimit=8, accept_any=False)
    #solve_dfs2(level[0], steplimit=level[1])
    #play(level[0], [1, 2, 0, 2, 0, 0, 0, 1, 1, 1, 1, 1, 1, 3, 1, 1, 2, 1, 1, 2, 2, 0, 2, 0, 2, 2, 2, 2, 0, 2, 0, 2, 2, 2, 2, 3, 3, 3])