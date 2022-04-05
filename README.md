# Crossword introduction

Crossword is an Artificial Intelligence that generates crossword puzzles.

Giving the AI one file containing a library of words, and another file containing the desired structure of the crossword, the AI will figure out whether it is possible or not to generate a crossword with the given data. If possible, a crossword will be generated.

The main algorithm of the a AI is an instance of a Constraint Satisfaction Problem (CSR). More specificaly, it uses a Backtracking Search algorithm, together with a number of optimizations and heuristics in order to solve the task quicker, including:

- Unary Node Consistency is enforced before the backtrack algorithm runs.
- Binary Arc Consistency is enforced with an AC-3 algorithm before the backtrack algorithm runs.
- Domain values for each variable (possible words) are ordered according to the least-constraining values heuristic.
- Unassigned variables are evaluated according to: first, the minimum remaining value heuristic, and secondly, the degree heuristic.

# Usage

## Dependencies

Crossword uses the Pillow library for generating images of the crosswords. The Pillow library can be installed by means of the `requirements.txt` file by running:

```
pip install -r requirements.txt
```

## Running the AI

The general command for running the AI is:

```
python generate.py <crossword_structure_file.txt> <words_file.txt> <output_file.png>
```

The output file is optional, and if used, will generate an image with the crossword (if possible).

There are some examples of structures and word files provided in the project, under the `./data/` directory. If using those files, the command to run the AI could for instance be:

```
python generate.py data/structure1.txt data/words1.txt output.png
```

Have fun generating crosswords!

# Intellectual Property Rights

MIT
