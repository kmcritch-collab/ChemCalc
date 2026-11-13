from bakery import assert_equal
from main import convert_to_moles


def test_convert_to_moles():
    """Test converting grams into moles."""

    assert_equal(convert_to_moles(10, 2.016), 4.9603174603174605)
    assert_equal(convert_to_moles(40, 32.00), 1.25)
    assert_equal(convert_to_moles(0, 18.015), 0.0)
    assert_equal(convert_to_moles(-5, 18.015), 0)
    assert_equal(convert_to_moles(10, 0), 0)


test_convert_to_moles()

from main import Reactant, convert_to_moles

hydrogen = Reactant(
    "H2",
    2,
    10,
    2.016,
    convert_to_moles(10, 2.016)
)

print(hydrogen.moles_available)

from main import create_reactant

def test_create_reactant():
    """Test creating a reactant using ChemPy."""
    hydrogen = create_reactant("H2", 2, 10)

    assert hydrogen.formula == "H2"
    assert hydrogen.coefficient == 2
    assert_equal(hydrogen.starting_mass, 10)
    assert_equal(hydrogen.moles_available, 10 / hydrogen.molar_mass)

test_create_reactant()

from main import create_reactant, find_limiting_reactant


def test_find_limiting_reactant():
    """Test finding the limiting reactant."""

    hydrogen = create_reactant("H2", 2, 10)
    oxygen = create_reactant("O2", 1, 40)

    reactants = [hydrogen, oxygen]

    limiting = find_limiting_reactant(reactants)

    assert limiting.formula == "H2"

    print("Limiting reactant test passed!")


test_find_limiting_reactant()