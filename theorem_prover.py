MAX_CONSTANTS = 10

PROPOSITION = ["p", "q", "r", "s"]
NEGATED_PROPOSITION = [f"-{p}" for p in PROPOSITION]
BINARY_CONNECTIVE = [">", "v", "^"]
VARIABLES = ["x", "y", "z", "w"]
PREDICATES = ["P", "Q", "R", "S"]
ATOMS = [f"{p}({v1},{v2})" for p in PREDICATES for v1 in VARIABLES for v2 in VARIABLES]
NEGATED_ATOMS = [f"-{a}" for a in ATOMS]

PROPOSITIONAL_LOGIC = PROPOSITION + BINARY_CONNECTIVE + ["-", "(", ")"]
FIRST_ORDER_LOGIC = (
    VARIABLES + PREDICATES + BINARY_CONNECTIVE + ["-", "(", ")", " ", ",", "E", "A"]
)

ALPHA = ["^", "--", "-v", "->"]
BETA = ["v", "-^", ">"]
DELTA = ["E", "-A"]
GAMMA = ["A", "-E"]

CONSTANTS = [chr(x) for x in range(ord("a"), ord("j") + 1)]

PICKED = []


class NotAFormula(Exception):
    pass


class TooManyConstants(Exception):
    pass


class AllClosedTermsPicked(Exception):
    pass


def _first_order(fmla):
    if fmla == "":
        return False
    for char in fmla:
        if char not in FIRST_ORDER_LOGIC:
            return False
    try:
        if parse(fmla) == 0:
            return False
        else:
            return True
    except NotAFormula:
        return False


def _prop_formula(fmla):
    if fmla == "":
        return False
    for char in fmla:
        if char not in PROPOSITIONAL_LOGIC:
            return False
    try:
        if parse(fmla) == 0:
            return False
        else:
            return True
    except NotAFormula:
        return False


def _main_connective(fmla):
    parenthesis_scope = []
    for count, char in enumerate(fmla):
        if char in BINARY_CONNECTIVE and len(parenthesis_scope) == 1:
            return count
        elif char == "(":
            parenthesis_scope.append("a")
        elif char == ")":
            try:
                parenthesis_scope.pop()
            except:
                raise NotAFormula
    raise NotAFormula


def parse(fmla):
    if fmla in PROPOSITION:  # Return "A proposition" if formula is a proposition.
        return 6

    elif (
        fmla in NEGATED_PROPOSITION
    ):  # Return "Negated propositional formula" if formula is a negated proposition.
        return 7

    elif fmla in ATOMS:  # Return "an atom" if the formula is an atom.
        return 1

    elif (
        fmla[0] == "E" and fmla[1] in VARIABLES
    ):  # Return "an existentially quantified formula" if whatever follows after "Ex" is a first order formula,
        # else return "not a formula".]
        if _first_order(fmla[2:]):
            return 4
        else:
            return 0
    elif (
        fmla[0] == "A" and fmla[1] in VARIABLES
    ):  # Return "an universally quantified formula" if whatever follows after "Ax" is a first order formula,
        # else return "not a formula".
        if _first_order(fmla[2:]):
            return 3
        else:
            return 0

    elif (
        fmla[0] == "-"
    ):  # Return "a negation of a first order logic formula" if whatever follows after "-" is a first order formula,
        # return "a negation of a propositional formula" if whatever follows after "-" is a propositional formula.
        if _first_order(fmla[1:]):
            return 2
        if _prop_formula(fmla[1:]):
            return 7
        else:
            return 0

    elif fmla[0] == "(":
        try:
            index = _main_connective(fmla)
        except NotAFormula:
            return 0

        if _first_order(fmla[1:index]) and _first_order(
            fmla[index + 1 : len(fmla) - 1]
        ):
            return 5

        elif _prop_formula(fmla[1:index]) and _prop_formula(
            fmla[index + 1 : len(fmla) - 1]
        ):
            return 8

        else:
            return 0
    else:
        return 0


# Return the LHS of a binary connective formula
def lhs(fmla):
    return fmla[1 : _main_connective(fmla)]


# Return the connective symbol of a binary connective formula
def con(fmla):
    return f"{fmla[_main_connective(fmla)]}"


# Return the RHS symbol of a binary connective formula
def rhs(fmla):
    return fmla[_main_connective(fmla) + 1 : len(fmla) - 1]


def expanded(theory, literal_count=0):
    adjust_theory(theory)
    for count, element in enumerate(theory):
        try:
            tableau_case(element)
            for char in ["E", "A"]:
                if char in element:
                    continue
        except NotAFormula:
            literal_count += 1
        if count + 1 == len(theory):
            return True if literal_count == len(theory) else False


def contradictory(tableau):
    for count, element in enumerate(tableau):
        if element[0] != "-":
            if f"-{element}" in tableau[count + 1 : len(tableau)]:
                return True
        if element[0] == "-":
            if element[1:] in tableau[count + 1 : len(tableau)]:
                return True
    return False


# You may choose to represent a theory as a set or a list
def theory(fmla):  # initialise a theory with a single formula in it
    theory = [fmla]
    return theory


def pick_non_literal(theory):
    theory = adjust_theory(theory)
    for element in theory:
        try:
            tableau_case(element)
            return element
        except NotAFormula:
            continue


def closed_terms(tableau):
    tableau_sum = list_sum(list_sum(tableau))
    closed_terms = []
    for char in tableau_sum:
        if char in VARIABLES + CONSTANTS:
            closed_terms.append(char)
    return list(set(closed_terms))


def alpha(phi, theory, case):
    if case == "^":
        theory.insert(0, lhs(phi))
        theory.insert(0, rhs(phi))
    elif case == "->":
        theory.insert(0, lhs(phi)[1:])
        theory.insert(0, f"-{rhs(phi)}")
    elif case == "--":
        theory.insert(0, phi[2:])
    elif case == "-v":
        theory.insert(0, f"-{lhs(phi)[1:]}")
        theory.insert(0, f"-{rhs(phi)}")
    return theory


def beta(phi, theory):
    theory.insert(0, phi)
    return theory


def delta(phi, theory, constant, bound_var):
    for count, char in enumerate(phi):
        if char == bound_var:
            phi = phi[:count] + constant + phi[count + 1 :]
    theory.insert(0, phi)
    return theory


def gamma(phi, theory, bound_var, closed_terms):
    for i in CONSTANTS + closed_terms:
        new_phi = phi
        for count, char in enumerate(phi):
            if char == bound_var:
                new_phi = new_phi[:count] + i + new_phi[count + 1 :]
        theory.insert(0, new_phi)
    return theory


def tableau_case(phi):
    if phi[0] == "-" and phi[1] == "-":
        return "--"
    if phi[0] == "E":
        return "E"
    if phi[0] == "-" and phi[1] == "A":
        return "-A"
    if phi[0] == "A":
        return "A"
    if phi[0] == "-" and phi[1] == "E":
        return "-E"
    if phi[0] == "-":
        return f"-{con(phi)}"
    else:
        return con(phi)


def list_sum(_list):
    sum_list = []
    for count, char in enumerate(_list):
        sum_list += _list[count]
    return sum_list


def adjust_theory(theory):
    for element in theory:
        adjust(element)
    return theory


def adjust(phi):
    for count, char in enumerate(phi):
        if char in CONSTANTS:
            phi = phi[:count] + "x" + phi[count + 1 :]
    return phi


def lhs_rhs(phi, case):
    if case == "v":
        _lhs = lhs(phi)
        _rhs = rhs(phi)
    if case == ">":
        _lhs = f"-{lhs(phi)}"
        _rhs = rhs(phi)
    if case == "-^":
        _lhs = f"-{lhs(phi)[1:]}"
        _rhs = f"-{rhs(phi)}"
    return _lhs, _rhs


def add_theory(theory, tableau):
    if theory not in tableau and not contradictory(theory):
        tableau.insert(0, theory)


# check for satisfiability
def sat(tableau):
    global PICKED
    if not _prop_formula(tableau[0][0]) and not _first_order(tableau[0][0]):
        return 0
    while len(tableau) != 0:
        terms = closed_terms(tableau)
        theory = tableau.pop(0)
        if expanded(theory) and not contradictory(theory):
            PICKED = []
            return 1
        else:
            theory_copy = theory.copy()
            phi = pick_non_literal(theory_copy)
            try:
                case = tableau_case(phi)
            except NotAFormula:
                adjusted_phi = adjust(phi)
                case = tableau_case(adjusted_phi)
            theory.remove(phi)

            if case in ALPHA:
                theory = alpha(phi, theory, case)
                add_theory(theory, tableau)

            if case in BETA:
                _lhs, _rhs = lhs_rhs(phi, case)

                theory_1 = beta(_lhs, theory.copy())
                theory_2 = beta(_rhs, theory.copy())

                add_theory(theory_1, tableau)
                add_theory(theory_2, tableau)

            if case in DELTA:
                try:
                    constant = CONSTANTS[len(PICKED)]
                    PICKED.append(CONSTANTS[len(PICKED)])
                except IndexError:
                    PICKED = []
                    return 2

                if case == "E":
                    theory = delta(phi[2:], theory, constant, phi[1])
                if case == "-A":
                    theory = delta(f"-{phi[3: len(phi)]}", theory, constant, phi[2])
                add_theory(theory, tableau)
            if case in GAMMA:
                if case == "A":
                    theory = gamma(phi[2:], theory, phi[1], terms)
                if case == "-E":
                    theory = gamma(f"-{phi[3 : len(phi)]}", theory, phi[2], terms)

                add_theory(theory, tableau)
    PICKED = []
    return 0


# DO NOT MODIFY THE CODE BELOW
f = open("testfile.txt")

parseOutputs = [
    "not a formula",
    "an atom",
    "a negation of a first order logic formula",
    "a universally quantified formula",
    "an existentially quantified formula",
    "a binary connective first order formula",
    "a proposition",
    "a negation of a propositional formula",
    "a binary connective propositional formula",
]

satOutput = ["is not satisfiable", "is satisfiable", "may or may not be satisfiable"]

firstline = f.readline()

PARSE = False
if "PARSE" in firstline:
    PARSE = True

SAT = False
if "SAT" in firstline:
    SAT = True

for line in f:
    if line[-1] == "\n":
        line = line[:-1]
    parsed = parse(line)

    if PARSE:
        output = "%s is %s." % (line, parseOutputs[parsed])
        if parsed in [5, 8]:
            output += (
                " Its left hand side is %s, its connective is %s, and its right hand side is %s."
                % (lhs(line), con(line), rhs(line))
            )
        print(output)

    if SAT:
        if parsed:
            tableau = [theory(line)]
            print("%s %s." % (line, satOutput[sat(tableau)]))
        else:
            print("%s is not a formula." % line)
