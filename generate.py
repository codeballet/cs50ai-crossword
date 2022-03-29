from cmath import inf
import copy
from email.policy import default
import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains_copy = copy.deepcopy(self.domains)
        for variable, domain in domains_copy.items():
            for word in domain:
                if len(word) != variable.length:
                    # remove words where length does not match variable
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        # get indexes of overlap between x and y
        x_index, y_index = self.crossword.overlaps[x, y]

        # set of values to delete from x's domain
        to_delete = set()

        # step through x's domain values
        for x_word in self.domains[x]:
            satisfied = False
            # check for value in y's domain to satisfy restrictions
            for y_word in self.domains[y]:
                if x_word[x_index] == y_word[y_index]:
                    # overlap found, restriction satisfied
                    satisfied = True
                    break
            if not satisfied:
                to_delete.add(x_word)
                revised = True

        if revised:
            # delete words that did not satisfy restrictions
            for word in to_delete:
                self.domains[x].remove(word)
                    
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            # create queue of all arcs
            arcs = list()
            edges = self.crossword.overlaps
            for vars, overlap in edges.items():
                if overlap != None:
                    arcs.append(vars)

        if len(arcs) != 0:
            # check an arc for arc-consistency
            x, y = arcs.pop()
            if self.revise(x, y):
                # domain of x arc-consistent in relation to y
                if len(self.domains[x]) == 0:
                    # x's domain is empty, problem cannot be solved
                    return False
                # for each neighbour z to x, excluding y, add (z,x) to queue
                for arc in arcs:
                    if arc[0] == x and arc[1] != y:
                        arcs.append((arc[1], arc[0]))
            # recursive call to function
            self.ac3(arcs)

        # queue empty, arc consistency enforced
        return True
            

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        result = True
        # get all variables
        variables = set(self.domains.keys())
        for v in variables:
            if assignment.get(v) == None:
                # assignment incomplete
                result = False
        return result

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        result = True

        # check if all words are distinct
        for v1, e1 in assignment.items():
            for v2, e2 in assignment.items():
                if v1 == v2:
                    continue
                if e1 == e2:
                    result = False

        # check if every word is of correct length
        for v, e in assignment.items():
            if v.length != len(e):
                result = False

        # check for conflicts between neighbouring words
        edges = self.crossword.overlaps
        for vars, overlap in edges.items():
            # step through all existing overlaps
            if overlap != None:
                # find overlap in assignment
                for a1 in assignment.keys():
                    for a2 in assignment.keys():
                        if a1 != a2:
                            if a1 == vars[0] and a2 == vars[1]:
                                # neighbour overlap found
                                assigned_word = assignment[a1]
                                neighbour_word = assignment[a2]
                                i_assigned = overlap[0]
                                i_neighbour = overlap[1]
                                # check if overlap in assignment matches
                                if assigned_word[i_assigned] != neighbour_word[i_neighbour]:
                                    # conflict found
                                    result = False

        return result

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # dict for how many choices are eliminated for each word
        word_elimination = dict()
        # dict for the sorted domain of var
        sorted_domain = dict()

        # get neighbours not already assigned
        neighbours = dict()
        edges = self.crossword.overlaps
        for vars, overlap in edges.items():
            if overlap != None and vars[0] == var and vars[1] not in assignment:
                neighbours[vars[1]] = overlap

        # count how many choices each word eliminates for neighbours
        if len(neighbours) != 0:
            # step through the domain of words for var
            for var_word in self.domains[var]:
                # set counter for number of restrictions
                n = 0
                for neighbour, overlap in neighbours.items():
                    # get each neighbour's domain
                    neighbour_domain = self.domains[neighbour]
                    for neighbour_word in neighbour_domain:
                        # check if var's word matches neighbour's word
                        if var_word[overlap[0]] != neighbour_word[overlap[1]]:
                            # restriction not satisfied, increase counter
                            n += 1
                # update minimum count and best word
                word_elimination[var_word] = n
            # sort var's domain
            sorted_domain = sorted(word_elimination, key=lambda word: word_elimination[word])
        else:
            # no relevant neighbours, no sorting necessary
            sorted_domain = self.domains[var]

        return sorted_domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # get all variables
        variables = set(self.domains.keys())
        for v in variables:
            if v not in assignment:
                # return a variable not yet assigned
                return v

        # all variables assigned
        return None


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # if assignment is complete, return assignment
        if self.assignment_complete(assignment):
            return assignment

        # select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # step through the domain values for the variable
        for value in self.order_domain_values(var, assignment):
            # add to assignment and check if consistent
            assignment[var] = value
            if self.consistent(assignment):
                # recursively call backtrack function
                result = self.backtrack(assignment)
                if result != None:
                    # assignment completed
                    return result
            # domain value not consistent, remove from assignment
            del assignment[var]
        # failed to find solution
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
