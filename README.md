# 8Puzzle
Project assignment for COMS W4701 Artificial Intelligence at Columbia University.  Project description taken from Prof. Ansaf Salleb Ouissi as follows: 

The N-puzzle game consists of a board holding N = m2 − 1 distinct movable tiles, plus one empty space. There is
one tile for each number in the set {0, 1,..., m2 − 1}. In this assignment, we will represent the blank space with the
number 0 and focus on the m = 3 case (8-puzzle).
In this combinatorial search problem, the aim is to get from any initial board state to the configuration with all
tiles arranged in ascending order {0, 1,..., m2 − 1} – this is your goal state. The search space is the set of all possible
states reachable from the initial state. Each move consists of swapping the empty space with a component in one of
the four directions {‘Up’, ‘Down’, ‘Left’, ‘Right’}. Give each move a cost of one. Thus, the total cost of a path will
be equal to the number of moves made.

I implemented the following artificial intelligence algorithms to search for a solution to the problem: breadth first search, depth first search, A* search 
