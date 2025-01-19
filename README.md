# **Untitled Block Game Solver**

This is a solver for my puzzle game [Untitled Block Game](https://github.com/ttahelenius/untitled-block-game). Large part of the challenge in later levels involves optimizing the steps used, so this project was born out of curiosity for what might be the most optimal solution.
The solver uses a hybrid method combining breadth-first search and depth-first search, refer to [Technical Details](#technical-details) for more details.

## **Installation**

```bash
git clone https://github.com/ttahelenius/untitled-block-game-solver.git
```

Note: Python 3.9+ required.

## **Usage**

At the end of the file there are some levels[^1] to choose from depending on which line of code is uncommented.
The ```solve``` function attempts to find a solution on the given level and, if found, returns the solution as a list of integers 0-3 representing the inputs right, up, left and down in order.
This solution can be given to the ```play``` function which prints the solution state by state in ASCII art, resulting in an animation. Currently level4 seems to require so many moves that it's practically beyond the cababilities of the solver.

Note: Solving level3 is configured to use upwards of 10 GB of RAM.

## **Technical Details**

The game features at most four possible moves at each game state, the problem therefore is equivalent to finding the shortest path from the starting game state to a winning one in a directed graph consisting of game states as the nodes and moves as the arcs.
The algorithm performs a breadth-first search (bfs) skipping the already visited nodes. Then, after a threshold (indicated by the parameter in the ```solve``` function) it switches to a depth-first search (dfs). This combines the best features of each one:
* The bfs part revisits no nodes but its memory use grows exponentially as a function of moves made
* The later dfs is a lot faster for short paths and takes virtually no further memory but can end up running around in circles.

A seemingly optimal threshold has been chosen for each example level but the downside is that it cannot be known in advance. A suboptimal choice will result in exponentially worse performance so some manual trial and error is often required.

Note: Each level is defined with a step limit, which will serve a function in the game itself. Notice that only some of the moves are steps. The algorithm, however, is constructed in such a way that steps are prioritized i.e. the found solution adheres to the step limit but doesn't contain unnecessary moves.

## **Further Considerations**

I've rewritten this solver in many different languages before, this time Python was selected as it allows for rapid prototyping for algorithmic optimizations. Admittedly for memory use and speed it's not the optimal choice.
Furthermore manual inline of many functions was necessary to squeeze out more speed, which suggests maybe the next rewrite should be in C/C++ where inline is an inbuilt feature.
Nevertheless algorithmic optimizations will carry most of the weight here as there's only so much speed you can gain before the exponential catches up.

Frankly even in its current state the solver only begins to scratch the surface of what is really needed for most of the levels I've designed.
In some levels the number of required moves is an order of magnitude larger than the ones considered here, so an algorithm of exponential time complexity such as this will probably never suffice even if it was successfully implemented for parallel processing on a graphics card.

[^1]: These levels don't necessarily correspond to the levels in the game itself
