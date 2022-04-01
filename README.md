# Crossword

Crossword is an Artificial Intelligence that generates crossword puzzles.

Giving the AI one file containing a library of words, and another file containing the desired structure of the crossword, the AI will figure out whether it is possible or not to generate a crossword with the given data. If possible, a crossword will be generated.

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
