from __future__ import division
from __future__ import print_function

import sys
import math
import time
import queue as Q
import resource 


## The Class that Represents the Puzzle
class PuzzleState(object):
    """
        The PuzzleState stores a board configuration and implements
        movement instructions to generate valid children.
    """
    action_order = {"Up": 0, "Down": 1, "Left": 3, "Right": 4}

    def __init__(self, config, n, parent=None, action="Initial", cost=0):
        """
        :param config->List : Represents the n*n board, for e.g. [0,1,2,3,4,5,6,7,8] represents the goal state.
        :param n->int : Size of the board
        :param parent->PuzzleState
        :param action->string
        :param cost->int
        """
        if n*n != len(config) or n < 2:
            raise Exception("The length of config is not correct!")
        if set(config) != set(range(n*n)):
            raise Exception("Config contains invalid/duplicate entries : ", config)

        self.n        = n
        self.cost     = cost
        self.parent   = parent
        self.action   = action
        self.action_value = PuzzleState.action_order.get(action, -1)
        self.config   = config
        self.children = []

        # Get the index and (row, col) of empty block
        self.blank_index = self.config.index(0)

    def display(self):
        """ Display this Puzzle state as a n*n board """
        for i in range(self.n):
            print(self.config[3*i : 3*(i+1)])

    def move_up(self):
        """ 
        Moves the blank tile one row up.
        :return a PuzzleState with the new configuration
        """
        place = self.config.index(0) 
        if place < 3: return None 
        else: 
            letter = self.config[place-3]
            newConfig = self.config.copy()
            newConfig[place] = letter 
            newConfig[place-3] = 0
            return PuzzleState(newConfig, self.n, self, "Up", self.cost + 1)
      
    def move_down(self):
        """
        Moves the blank tile one row down.
        :return a PuzzleState with the new configuration
        """
        place = self.config.index(0)
        if place >= 6: return None 
        else:
            letter = self.config[place+3]
            newConfig = self.config.copy()
            newConfig[place] = letter 
            newConfig[place+3] = 0
            return PuzzleState(newConfig, self.n, self, "Down", self.cost + 1)
      
    def move_left(self):
        """
        Moves the blank tile one column to the left.
        :return a PuzzleState with the new configuration
        """
        place = self.config.index(0)
        if place % 3 == 0: return None 
        else: 
            letter = self.config[place-1]
            newConfig = self.config.copy()
            newConfig[place] = letter
            newConfig[place-1] = 0
            return PuzzleState(newConfig, self.n, self, "Left", self.cost + 1)

    def move_right(self):
        """
        Moves the blank tile one column to the right.
        :return a PuzzleState with the new configuration
        """
        place = self.config.index(0)
        if place % 3 == 2: return None 
        else: 
            letter = self.config[place+1]
            newConfig = self.config.copy()
            newConfig[place] = letter 
            newConfig[place+1] = 0
            return PuzzleState(newConfig, self.n, self, "Right", self.cost + 1)
      
    def expand(self):
        """ Generate the child nodes of this node """
        
        # Node has already been expanded
        if len(self.children) != 0:
            return self.children
        
        # Add child nodes in order of UDLR
        children = [
            self.move_up(),
            self.move_down(),
            self.move_left(),
            self.move_right()]

        # Compose self.children of all non-None children states
        self.children = [state for state in children if state is not None]
        return self.children
    
class QueueFrontier(): 
    def __init__(self): 
        self.queue = []

    def add(self, state: PuzzleState): 
        if state not in self.queue: 
            self.queue.append(state)

    def remove(self): 
        return self.queue.pop(0)

class StackFrontier(): 
    def __init__(self): 
        self.stack = []
        #use set to make sure we do not queue same configuration twice 
        self.set = set()
    
    def add(self, state):
        if state not in self.stack: 
            self.stack.append(state)
        if tuple(state.config) not in self.set: 
            self.set.add(tuple(state.config))

    def remove(self):
        if len(self.stack) > 0: 
            element = self.stack.pop() 
        if len(self.set) > 0: 
            self.set.remove(tuple(element.config))
        return element
    
class PriorityQueue(): 
    def __init__(self): 
        #queue will store (state, h) where h is heuristic 
        self.queue = []
        #use set to make sure we do not queue same configuration twice 
        self.set = set()

    def add(self, state: PuzzleState): 
        #calc heuristic using manhattan dist 
        h = calculate_total_cost(state)
        if (state, h) not in self.queue: 
            self.queue.append((state, h))   
        if tuple(state.config) not in self.set:
            self.set.add(tuple(state.config))

    def remove(self): 
        #return element if remove is successful
        if len(self.queue) > 0: 
            self.queue.sort(key = lambda x: (x[1]+x[0].cost, x[0].action_order))
            element = self.queue.pop(0)[0]
        if len(self.set) > 0: 
            self.set.remove(tuple(element.config))
        return element

# Function that Writes to output.txt
def writeOutput(path, cost, nodes_expanded, search_depth, max_search_depth, running_time, max_ram_usage):
    with open("output.txt", "w") as file: 
        file.write("path_to_goal:  {}\n".format(path))
        file.write("cost_of_path: {}\n".format(cost))
        file.write("nodes_expanded: {}\n".format(nodes_expanded))
        file.write("search_depth: {}\n".format(search_depth))
        file.write("max_search_depth: {}\n".format(max_search_depth))
        file.write("running_time: {:.8f}\n".format(running_time))
        file.write("max_ram_usage: {:.8f}\n".format(max_ram_usage))
    pass

def bfs_search(initial_state, start_time):
    """BFS search"""
    bfs_start_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    max_search_depth = 0 
    explored = set()
    frontier = QueueFrontier()
    frontier.add(initial_state)
    while frontier.queue != []:
        state = frontier.remove()
        if test_goal(state.config): 
            #write to output 
            bfs_ram = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - bfs_start_ram) / (2**20)
            writeOutput(getPath(state), state.cost, len(explored), state.cost, max_search_depth,  time.time()-start_time, bfs_ram)
            break 
        else: 
            if tuple(state.config) not in explored and state not in frontier.queue: 
                explored.add(tuple(state.config))
                state.expand()       
        for child in state.children: 
            #add child to frontier 
            if tuple(child.config) not in explored and child not in frontier.queue:
                frontier.add(child)
            #update max search depth 
            if child.cost > max_search_depth: 
                max_search_depth = child.cost


def dfs_search(initial_state, start_time):
    """DFS search"""
    dfs_start_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    max_search_depth = initial_state.cost
    explored = set()
    frontier = StackFrontier()
    frontier.add(initial_state)
    while frontier.stack != []:
        state = frontier.remove()
        #update max_search_depth 
        if state.cost > max_search_depth: 
            max_search_depth = state.cost
        if test_goal(state.config): 
            dfs_ram = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - dfs_start_ram) / (2**20)
            writeOutput(getPath(state), state.cost, len(explored), state.cost, max_search_depth, time.time()-start_time, dfs_ram)
            break 
        else: 
            if tuple(state.config) not in explored and tuple(state.config) not in frontier.set: 
                explored.add(tuple(state.config))
                state.expand()
        for child in state.children[::-1]: 
            #add child to frontier if config isn't there alr 
            if tuple(child.config) not in explored and tuple(child.config) not in frontier.set:
                frontier.add(child)

def A_star_search(initial_state, start_time):
    """A * search"""
    ### STUDENT CODE GOES HERE ###
    astar_start_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    max_search_depth = 0 
    explored = set()
    frontier = PriorityQueue()
    frontier.add(initial_state)
    while frontier.queue != []: 
        state = frontier.remove()
        if test_goal(state.config):
            #write to output 
            astar_ram = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - astar_start_ram) / (2**20)
            writeOutput(getPath(state), state.cost, len(explored), state.cost, max_search_depth, time.time()-start_time, astar_ram)
            break  
        elif tuple(state.config) not in explored and tuple(state.config) not in frontier.set: 
            explored.add(tuple(state.config))
            state.expand()
        for child in state.children: 
            #add child to frontier 
            if tuple(child.config) not in explored and tuple(child.config) not in frontier.set: 
                frontier.add(child)
            #update max search depth 
            if child.cost > max_search_depth: 
                max_search_depth = child.cost
        #if len(explored)>10: break 

def calculate_total_cost(state: PuzzleState):
    """calculate the total estimated cost of a state"""
    h = 0 
    for i, tile in enumerate(state.config):  
        h += calculate_manhattan_dist(i, tile, state.n)
    return h

def calculate_manhattan_dist(idx, value, n):
    """calculate the manhattan distance of a tile"""
    rowDistance = abs(getRow(idx) - getRow(value))
    columnDistance = abs(getColumn(idx) - getColumn(value))
    return rowDistance + columnDistance

def test_goal(state):
    """test the state is the goal state or not"""
    return state == [0,1,2,3,4,5,6,7,8]

def getRow(idx): 
    if idx in [0,1,2]: 
        return 0 
    if idx in [3,4,5]: 
        return 1 
    else: 
        return 2 
    
def getColumn(idx): 
    return idx%3 

def getPath(state): 
    #get path of current state from root node 
    path = []
    while state.parent is not None: 
        path.insert(0, state.action)
        state = state.parent
    return path

# Main Function that reads in Input and Runs corresponding Algorithm
def main():
    search_mode = sys.argv[1].lower()
    begin_state = sys.argv[2].split(",")
    begin_state = list(map(int, begin_state))
    board_size  = int(math.sqrt(len(begin_state)))
    hard_state  = PuzzleState(begin_state, board_size)
    start_time  = time.time()
    
    if   search_mode == "bfs": bfs_search(hard_state, start_time)
    elif search_mode == "dfs": dfs_search(hard_state, start_time)
    elif search_mode == "ast": A_star_search(hard_state, start_time)
    else: 
        print("Enter valid command arguments !")
        
    end_time = time.time()
    print("Program completed in %.3f second(s)"%(end_time-start_time))

if __name__ == '__main__':
    main()
