from gantry.util.spec import spec_variants


def test_valid_spec():
    """Test a valid spec string to be parsed"""
    assert spec_variants(
        "+adios2~advanced_debug patches=02253c7,acb3805,b724e6a use_vtkm=on"
    ) == {
        "adios2": True,
        "advanced_debug": False,
        "patches": ["02253c7", "acb3805", "b724e6a"],
        "use_vtkm": "on",
    }


def test_invalid_spec():
    """Test some invalid specs"""
    assert spec_variants("fefj!@#$%^&eifejifeifeij---5893843$%^&*()") == {}
    assert spec_variants("fifheife") == {}
    assert spec_variants("++++++") == {}
    assert spec_variants("+~~++") == {}
