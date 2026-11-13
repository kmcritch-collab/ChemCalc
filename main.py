from drafter import *
from dataclasses import dataclass
from chempy import Substance
import re
import inspect

set_site_information(
    author="Your Name",
    description=(
        "ChemCalc is a chemical reaction assistant "
        "that calculates limiting reactants, theoretical "
        "yield, percent yield, and remaining reactant masses."
    ),
    sources=[
        "ChemPy",
        "OpenStax Chemistry 2e, Chapter 4"
    ],
    planning="planning.md",
    links=[]
)

# Stores information about one chemical reactant.
@dataclass
class Reactant:
    formula: str
    coefficient: int
    starting_mass: float
    molar_mass: float
    moles_available: float


# Stores the results of one completed reaction.
@dataclass
class ReactionResult:
    """Store the results of a completed chemical reaction."""

    equation: str
    limiting_reactant: str
    theoretical_yield: float
    actual_yield: float
    percent_yield: float
    remaining_masses: list[float]


# Stores information used throughout the website.
@dataclass
class State:
    equation: str
    product_formula: str
    reactant_masses_text: str
    actual_yield_text: str
    reactants: list[Reactant]
    history: list[ReactionResult]
    message: str
    latest_result: ReactionResult | None
    reactant_results: list[str]
    
def convert_to_moles(mass: float, molar_mass: float) -> float:
    """Convert a substance's mass in grams into moles."""

    if mass < 0:
        return 0

    if molar_mass <= 0:
        return 0

    moles = mass / molar_mass

    return moles

def create_reactant(formula: str, coefficient: int, starting_mass: float) -> Reactant:
    """Create a Reactant using ChemPy to calculate molar mass."""
    if coefficient <= 0:
        raise ValueError("The coefficient must be positive.")
    if starting_mass < 0:
        raise ValueError("The starting mass cannot be negative.")

    substance = Substance.from_formula(formula)
    molar_mass = float(substance.mass)
    moles_available = convert_to_moles(starting_mass, molar_mass)

    return Reactant(
        formula,
        coefficient,
        starting_mass,
        molar_mass,
        moles_available
    )

def parse_equation(
    equation: str
) -> tuple[list[tuple[str, int]], str, int]:
    """Extract reactants and one product from a balanced equation."""

    if "->" not in equation:
        raise ValueError("Use -> between reactants and products.")

    sides = equation.split("->")

    if len(sides) != 2:
        raise ValueError("Enter exactly one reaction arrow.")

    reactant_parts = sides[0].split("+")
    product_parts = sides[1].split("+")

    if len(product_parts) != 1:
        raise ValueError("Please enter exactly one product.")

    def parse_compound(part: str) -> tuple[str, int]:
        """Extract a compound formula and its coefficient."""
        # Advanced technique: Regular expressions.
        # This pattern separates a chemical coefficient
        # from its molecular formula.
        # Group 1 captures the optional coefficient.
        # Group 2 captures the chemical formula.
        # The whitespace symbols allow spaces around compounds.
        match = re.fullmatch(
            r"\s*(\d*)\s*([A-Z][A-Za-z0-9()]*)\s*",
            part
        )

        if match is None:
            raise ValueError("Invalid chemical formula: " + part)

        coefficient_text = match.group(1)
        formula = match.group(2)

        coefficient = (
            int(coefficient_text)
            if coefficient_text
            else 1
        )

        if coefficient <= 0:
            raise ValueError("Coefficients must be positive.")

        return formula, coefficient

    reactants = [
        parse_compound(part)
        for part in reactant_parts
    ]

    product_formula, product_coefficient = (
        parse_compound(product_parts[0])
    )

    return reactants, product_formula, product_coefficient

def find_limiting_reactant(
    reactants: list[Reactant]
) -> Reactant:
    """Find the reactant that runs out first."""

    if len(reactants) == 0:
        raise ValueError("At least one reactant is required.")

    limiting_reactant = reactants[0]

    smallest_ratio = (
        limiting_reactant.moles_available /
        limiting_reactant.coefficient
    )

    for reactant in reactants:
        ratio = (
            reactant.moles_available /
            reactant.coefficient
        )

        if ratio < smallest_ratio:
            smallest_ratio = ratio
            limiting_reactant = reactant

    return limiting_reactant

def calculate_theoretical_yield(
    limiting_reactant: Reactant,
    product_coefficient: int,
    product_molar_mass: float
) -> float:
    """Calculate the maximum possible product mass in grams."""

    if product_coefficient <= 0:
        raise ValueError("Product coefficient must be positive.")

    if product_molar_mass <= 0:
        raise ValueError("Product molar mass must be positive.")

    if limiting_reactant.coefficient <= 0:
        raise ValueError("Reactant coefficient must be positive.")

    product_moles = (
        limiting_reactant.moles_available
        / limiting_reactant.coefficient
        * product_coefficient
    )

    theoretical_yield = product_moles * product_molar_mass

    return theoretical_yield

def calculate_percent_yield(
    actual_yield: float,
    theoretical_yield: float
) -> float:
    """Calculate the percent yield of a chemical reaction."""

    if actual_yield < 0:
        raise ValueError("Actual yield cannot be negative.")

    if theoretical_yield <= 0:
        raise ValueError("Theoretical yield must be positive.")

    percent_yield = (
        actual_yield / theoretical_yield
    ) * 100

    return percent_yield

def calculate_remaining_mass(
    reactant: Reactant,
    limiting_reactant: Reactant
) -> float:
    """Calculate the remaining mass of an unreacted reactant."""

    limiting_ratio = (
        limiting_reactant.moles_available /
        limiting_reactant.coefficient
    )

    consumed_moles = (
        limiting_ratio * reactant.coefficient
    )

    remaining_moles = (
        reactant.moles_available - consumed_moles
    )

    if remaining_moles < 0:
        remaining_moles = 0

    remaining_mass = remaining_moles * reactant.molar_mass

    return remaining_mass

def analyze_reaction(
    reactants: list[Reactant],
    product_formula: str,
    product_coefficient: int,
    actual_yield: float
) -> ReactionResult:
    """Perform a complete stoichiometry analysis."""

    if len(reactants) == 0:
        raise ValueError("At least one reactant is required.")

    if actual_yield < 0:
        raise ValueError("Actual yield cannot be negative.")

    limiting = find_limiting_reactant(reactants)

    product = Substance.from_formula(product_formula)
    product_molar_mass = float(product.mass)

    theoretical_yield = calculate_theoretical_yield(
        limiting,
        product_coefficient,
        product_molar_mass
    )

    percent_yield = calculate_percent_yield(
        actual_yield,
        theoretical_yield
    )

    remaining_masses = []

    for reactant in reactants:
        remaining_mass = calculate_remaining_mass(
            reactant,
            limiting
        )
        remaining_masses.append(remaining_mass)

    return ReactionResult(
        equation="Reaction analysis completed",
        limiting_reactant=limiting.formula,
        theoretical_yield=theoretical_yield,
        actual_yield=actual_yield,
        percent_yield=percent_yield,
        remaining_masses=remaining_masses
    )

def save_reaction(
    state: State,
    result: ReactionResult
) -> State:
    """Save a completed reaction and update the latest result."""

    state.history.append(result)
    state.latest_result = result
    state.message = "Reaction successfully saved!"

    return state

@route
def index(state: State) -> Page:
    """Display the ChemCalc homepage."""

    return Page(state, [
        Header("ChemCalc"),
        Header("Chemical Reaction Assistant", 2),
        Text(
            "Welcome to ChemCalc! "
            "Your interactive stoichiometry calculator."
        ),
        Header("What can ChemCalc do?", 3),
        BulletedList([
            "Find the limiting reactant.",
            "Calculate theoretical yield.",
            "Calculate percent yield.",
            "Determine remaining reactant mass."
        ]),
        Button("Learn Stoichiometry", "learn_stoichiometry"),
        Button("Start a Reaction", "reaction_input"),
        Button("View Reaction History", "reaction_history")
    ])


@route
def learn_stoichiometry(state: State) -> Page:
    """Explain the basic idea of stoichiometry."""

    return Page(state, [
        Header("Learning Stoichiometry"),
        Text(
            "Stoichiometry uses a balanced chemical equation "
            "to calculate the amounts of substances involved "
            "in a chemical reaction."
        ),
        Header("Important Concepts", 2),
        Text("Limiting Reactant: The reactant that runs out first."),
        Text("Theoretical Yield: The maximum amount of product possible."),
        Text("Percent Yield: Actual yield divided by theoretical yield, "
             "multiplied by 100."),
        Button("Return Home", "index"),
        Button("Start a Reaction", "reaction_input")
    ])


@route
def reaction_input(state: State) -> Page:
    """Display the chemical reaction input form."""

    return Page(state, [
        Header("Enter Your Chemical Reaction"),
        Text("Enter your balanced chemical equation."),
        TextBox("equation", state.equation),
        Text("Enter the product chemical formula."),
        TextBox("product_formula", state.product_formula),
        Text("Enter reactant masses in grams, one per line."),
        TextArea("reactant_masses_text", state.reactant_masses_text),
        Text("Enter the actual product mass collected in grams."),
        TextBox("actual_yield_text", state.actual_yield_text),
        Button("Submit Reaction", "submit_reaction"),
        Button("Return Home", "index")
    ])


@route
def submit_reaction(
    state: State,
    equation: str,
    product_formula: str,
    reactant_masses_text: str,
    actual_yield_text: str
) -> Page:
    """Process the submitted reaction and calculate its yields."""

    state.equation = equation
    state.product_formula = product_formula
    state.reactant_masses_text = reactant_masses_text
    state.actual_yield_text = actual_yield_text

    try:
        parsed_reactants, product, product_coefficient = (
            parse_equation(equation)
        )

        if product != product_formula.strip():
            raise ValueError(
                "Product formula does not match the equation."
            )

        masses = [
            float(line.strip())
            for line in reactant_masses_text.splitlines()
            if line.strip()
        ]

        if len(masses) != len(parsed_reactants):
            raise ValueError(
                "Enter exactly one mass for each reactant."
            )

        actual_yield = float(actual_yield_text)

        reactants = []

        for index, compound in enumerate(parsed_reactants):
            formula, coefficient = compound

            reactant = create_reactant(
                formula,
                coefficient,
                masses[index]
            )

            reactants.append(reactant)

        result = analyze_reaction(
            reactants,
            product,
            product_coefficient,
            actual_yield
        )

        result.equation = equation

        state.reactants = reactants
        state.reactant_results = []

        for index, reactant in enumerate(reactants):
            remaining = result.remaining_masses[index]

            state.reactant_results.append(
                reactant.formula
                + ": "
                + str(round(remaining, 3))
                + " g remaining"
            )

        save_reaction(state, result)

        return reaction_results(state)

    except (ValueError, TypeError) as error:
        state.message = "Calculation error: " + str(error)

        return Page(state, [
            Header("ChemCalc - Input Error"),
            Text(state.message),
            Button("Try Again", "reaction_input"),
            Button("Return Home", "index")
        ])
    
@route
def reaction_results(state: State) -> Page:
    """Display the completed chemical reaction analysis."""

    if state.latest_result is None:
        return Page(state, [
            Header("No Results Available"),
            Text("Please submit a chemical reaction first."),
            Button("Enter Reaction", "reaction_input")
        ])

    result = state.latest_result

    return Page(state, [
        Header("ChemCalc - Reaction Results"),
        Header("Reaction Summary", 2),

        Text("Balanced equation: " + result.equation),

        Header("Limiting Reactant", 3),
        Text("Limiting reactant: " + result.limiting_reactant),

        Header("Product Yield", 3),
        Text(
            "Theoretical yield: "
            + str(round(result.theoretical_yield, 3))
            + " g"
        ),
        Text(
            "Actual yield: "
            + str(round(result.actual_yield, 3))
            + " g"
        ),
        Text(
            "Percent yield: "
            + str(round(result.percent_yield, 2))
            + "%"
        ),

        Header("Remaining Reactants", 3),
        BulletedList(state.reactant_results),

        Button("Calculate Another Reaction", "reaction_input"),
        Button("View Reaction History", "reaction_history"),
        Button("Return Home", "index")
    ])


@route
def review_reaction(state: State) -> Page:
    """Display the reaction information entered by the user."""

    return Page(state, [
        Header("Review Your Reaction"),
        Text("Equation: " + state.equation),
        Text("Product: " + state.product_formula),
        Text("Reactant masses: " + state.reactant_masses_text),
        Text("Actual yield: " + state.actual_yield_text + " g"),
        Text(state.message),
        Button("Edit Reaction", "reaction_input"),
        Button("Return Home", "index")
    ])


@route
def reaction_history(state: State) -> Page:
    """Display previously completed chemical reactions."""

    history_items = []

    if len(state.history) == 0:
        history_items.append(
            Text("You have not completed any reactions yet.")
        )

    else:
        for index, result in enumerate(state.history):
            history_items.append(
                Header("Reaction " + str(index + 1), 2)
            )

            history_items.append(
                Text("Equation: " + result.equation)
            )

            history_items.append(
                Text(
                    "Limiting reactant: "
                    + result.limiting_reactant
                )
            )

            history_items.append(
                Text(
                    "Theoretical yield: "
                    + str(round(result.theoretical_yield, 3))
                    + " g"
                )
            )

            history_items.append(
                Text(
                    "Percent yield: "
                    + str(round(result.percent_yield, 2))
                    + "%"
                )
            )

    return Page(state, [
        Header("Reaction History"),
        *history_items,
        Button("Calculate Another Reaction", "reaction_input"),
        Button("Return Home", "index")
    ])

def create_test_state() -> State:
    """Create a fresh State for route testing."""

    return State(
        "",
        "",
        "",
        "",
        [],
        [],
        "Welcome to ChemCalc!",
        None,
        []
    )

def test_find_limiting_reactant() -> None:
    """Test finding the limiting reactant."""

    hydrogen = create_reactant("H2", 2, 10)
    oxygen = create_reactant("O2", 1, 40)

    reactants = [hydrogen, oxygen]

    limiting = find_limiting_reactant(reactants)

    assert limiting.formula == "O2"

    print("Limiting reactant test passed!")


test_find_limiting_reactant()

def test_calculate_theoretical_yield() -> None:
    """Test theoretical yield for hydrogen and oxygen producing water."""

    hydrogen = create_reactant("H2", 2, 10)
    oxygen = create_reactant("O2", 1, 40)

    reactants = [hydrogen, oxygen]

    limiting = find_limiting_reactant(reactants)

    water = Substance.from_formula("H2O")
    water_molar_mass = float(water.mass)

    result = calculate_theoretical_yield(
        limiting,
        2,
        water_molar_mass
    )

    assert abs(result - 45.0375) < 0.01

    print("Theoretical yield test passed!")
    print("Theoretical yield:", result, "grams")
    
test_calculate_theoretical_yield()

def test_calculate_percent_yield()-> None:
    """Test calculating percent yield."""

    result = calculate_percent_yield(38, 45.04)

    assert abs(result - 84.37) < 0.02

    print("Percent yield test passed!")
    print("Percent yield:", result, "%")
    
test_calculate_percent_yield()

def test_calculate_remaining_mass()-> None:
    """Test calculating the remaining mass of hydrogen."""

    hydrogen = create_reactant("H2", 2, 10)
    oxygen = create_reactant("O2", 1, 40)

    remaining = calculate_remaining_mass(
        hydrogen,
        oxygen
    )

    assert abs(remaining - 4.96) < 0.02

    print("Remaining mass test passed!")
    print("Hydrogen remaining:", remaining, "grams")
    
test_calculate_remaining_mass()

def test_analyze_reaction()-> None:
    """Test the complete stoichiometry analysis."""

    hydrogen = create_reactant("H2", 2, 10)
    oxygen = create_reactant("O2", 1, 40)

    reactants = [hydrogen, oxygen]

    result = analyze_reaction(
        reactants,
        "H2O",
        2,
        38
    )

    assert result.limiting_reactant == "O2"
    assert abs(result.theoretical_yield - 45.04) < 0.02
    assert abs(result.percent_yield - 84.37) < 0.02

    print("Complete reaction analysis test passed!")
    
test_analyze_reaction()

def test_save_reaction()-> None:
    """Test saving a completed reaction to history."""

    state = State(
        "",
        "",
        "",
        "",
        [],
        [],
        "Welcome to ChemCalc!",
        None,
        []
    )

    hydrogen = create_reactant("H2", 2, 10)
    oxygen = create_reactant("O2", 1, 40)

    result = analyze_reaction(
        [hydrogen, oxygen],
        "H2O",
        2,
        38
    )

    save_reaction(state, result)

    assert len(state.history) == 1
    assert state.history[0].limiting_reactant == "O2"

    print("Reaction history test passed!")
    
test_save_reaction()

def test_parse_equation()-> None:
    """Test extracting formulas and coefficients."""

    reactants, product, product_coefficient = (
        parse_equation("2H2 + O2 -> 2H2O")
    )

    assert reactants == [("H2", 2), ("O2", 1)]
    assert product == "H2O"
    assert product_coefficient == 2

    print("Equation parser test passed!")
    
test_parse_equation()

def test_reaction_history()-> None:
    """Test that completed reactions are stored in history."""

    state = State(
        "",
        "",
        "",
        "",
        [],
        [],
        "Welcome to ChemCalc!",
        None,
        []
    )

    hydrogen = create_reactant("H2", 2, 10)
    oxygen = create_reactant("O2", 1, 40)

    result = analyze_reaction(
        [hydrogen, oxygen],
        "H2O",
        2,
        38
    )

    result.equation = "2H2 + O2 -> 2H2O"

    save_reaction(state, result)

    assert len(state.history) == 1
    assert state.history[0].equation == "2H2 + O2 -> 2H2O"
    assert state.history[0].limiting_reactant == "O2"

    print("Reaction history display data test passed!")
    
test_reaction_history()

def test_index_route() -> None:
    """Test that the homepage loads successfully."""

    state = create_test_state()

    page = index(state)

    assert isinstance(page, Page)

    print("Homepage route test passed!")
    
def test_learn_stoichiometry_route() -> None:
    """Test that the learning page loads successfully."""

    state = create_test_state()

    page = learn_stoichiometry(state)

    assert isinstance(page, Page)

    print("Learning page route test passed!")
    
def test_reaction_input_route() -> None:
    """Test that the reaction input page loads."""

    state = create_test_state()

    page = reaction_input(state)

    assert isinstance(page, Page)

    print("Reaction input route test passed!")
    
def test_submit_reaction_route() -> None:
    """Test submitting a reaction through the website."""

    state = create_test_state()

    page = submit_reaction(
        state,
        "2H2 + O2 -> 2H2O",
        "H2O",
        "10\n40",
        "38"
    )

    assert isinstance(page, Page)
    assert state.equation == "2H2 + O2 -> 2H2O"
    assert state.product_formula == "H2O"
    assert len(state.history) == 1
    assert state.latest_result is not None
    assert state.latest_result.limiting_reactant == "O2"

    print("Submit reaction route test passed!")
    
def test_reaction_results_route() -> None:
    """Test displaying reaction results."""

    state = create_test_state()

    empty_page = reaction_results(state)

    assert isinstance(empty_page, Page)

    hydrogen = create_reactant("H2", 2, 10)
    oxygen = create_reactant("O2", 1, 40)

    result = analyze_reaction(
        [hydrogen, oxygen],
        "H2O",
        2,
        38
    )

    result.equation = "2H2 + O2 -> 2H2O"

    state.latest_result = result
    state.reactant_results = [
        "H2: 4.96 g remaining",
        "O2: 0 g remaining"
    ]

    page = reaction_results(state)

    assert isinstance(page, Page)
    assert state.latest_result.limiting_reactant == "O2"

    print("Reaction results route test passed!")
    
def test_review_reaction_route() -> None:
    """Test displaying the submitted reaction information."""

    state = create_test_state()

    state.equation = "2H2 + O2 -> 2H2O"
    state.product_formula = "H2O"
    state.reactant_masses_text = "10\n40"
    state.actual_yield_text = "38"
    state.message = "Reaction information submitted."

    page = review_reaction(state)

    assert isinstance(page, Page)
    assert state.equation == "2H2 + O2 -> 2H2O"
    assert state.product_formula == "H2O"

    print("Review reaction route test passed!")
    
def test_reaction_history_route() -> None:
    """Test displaying empty and populated reaction history."""

    state = create_test_state()

    empty_page = reaction_history(state)

    assert isinstance(empty_page, Page)

    hydrogen = create_reactant("H2", 2, 10)
    oxygen = create_reactant("O2", 1, 40)

    result = analyze_reaction(
        [hydrogen, oxygen],
        "H2O",
        2,
        38
    )

    result.equation = "2H2 + O2 -> 2H2O"

    save_reaction(state, result)

    page = reaction_history(state)

    assert isinstance(page, Page)
    assert len(state.history) == 1
    assert state.history[0].equation == "2H2 + O2 -> 2H2O"

    print("Reaction history route test passed!")
    
# Run all website route tests.
test_index_route()
test_learn_stoichiometry_route()
test_reaction_input_route()
test_submit_reaction_route()
test_reaction_results_route()
test_review_reaction_route()
test_reaction_history_route()
    
start_server(State(
    "",
    "",
    "",
    "",
    [],
    [],
    "Welcome to ChemCalc!",
    None,
    []
))





