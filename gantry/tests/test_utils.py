import pytest

from gantry.utils.misc import spec_variants

# write tests for spec_variants here
# +adios2~advanced_debug patches=02253c7,acb3805,b724e6a use_vtkm=on has to equal {}


@pytest.fixture
def variant_string():
    return "+adios2~advanced_debug patches=02253c7,acb3805,b724e6a use_vtkm=on"


def test_spec_variants(variant_string):
    assert spec_variants(variant_string) == {
        "adios2": True,
        "advanced_debug": False,
        "patches": ["02253c7", "acb3805", "b724e6a"],
        "use_vtkm": "on",
    }
