import pytest

from gantry.routes.prediction import prediction
from gantry.tests.defs import prediction as defs
from gantry.util.spec import parse_alloc_spec


@pytest.fixture
async def db_conn_inserted(db_conn):
    """Returns a connection to a database with 5 samples inserted"""

    with open("gantry/tests/sql/insert_samples.sql") as f:
        await db_conn.executescript(f.read())

    return db_conn


async def test_exact_match(db_conn_inserted):
    """All fields are an exact match for 5 samples in the database."""

    assert (
        await prediction.predict(db_conn_inserted, defs.NORMAL_BUILD)
        == defs.NORMAL_PREDICTION
    )


async def test_expensive_variants(db_conn_inserted):
    """
    Tests whether the algorithm filters by expensive variants.
    The input has been modified to prevent an exact match with
    any of the samples.
    """

    assert (
        await prediction.predict(db_conn_inserted, defs.EXPENSIVE_VARIANT_BUILD)
        == defs.NORMAL_PREDICTION
    )


async def test_no_variant_match(db_conn_inserted):
    """
    All fields match except for variants, expect default predictions with no sample.
    """

    assert (
        await prediction.predict(db_conn_inserted, defs.BAD_VARIANT_BUILD)
        == defs.DEFAULT_PREDICTION
    )


async def test_partial_match(db_conn_inserted):
    """
    Some of the fields match, so the prediction should be based on matching
    with other fields. In reality, we're using the same dataset but just
    testing that the prediction will be the same with a different compiler name.
    """

    # same as NORMAL_BUILD, but with a different compiler name to test partial matching
    diff_compiler_build = defs.NORMAL_BUILD.copy()
    diff_compiler_build["compiler_name"] = "gcc-different"

    assert (
        await prediction.predict(db_conn_inserted, diff_compiler_build)
        == defs.NORMAL_PREDICTION
    )


async def test_empty_sample(db_conn):
    """No samples in the database, so we expect default predictions."""

    assert (
        await prediction.predict(db_conn, defs.NORMAL_BUILD) == defs.DEFAULT_PREDICTION
    )


# Test validate_payload
def test_valid_spec():
    """Tests that a valid spec is parsed correctly."""
    assert parse_alloc_spec("emacs@29.2-test +json+native+treesitter%gcc@12.3.0") == {
        "pkg_name": "emacs",
        "pkg_version": "29.2-test",
        "pkg_variants": '{"json": true, "native": true, "treesitter": true}',
        "pkg_variants_dict": {"json": True, "native": True, "treesitter": True},
        "compiler_name": "gcc",
        "compiler_version": "12.3.0",
    }


def test_invalid_specs():
    """Test a series of invalid specs"""

    # not a spec
    assert parse_alloc_spec("hi") == {}

    # missing package
    assert parse_alloc_spec("@29.2 +json+native+treesitter%gcc@12.3.0") == {}

    # missing compiler
    assert parse_alloc_spec("emacs@29.2 +json+native+treesitter") == {}

    # variants not spaced correctly
    assert parse_alloc_spec("emacs@29.2+json+native+treesitter%gcc@12.3.0") == {}

    # missing compiler version
    assert parse_alloc_spec("emacs@29.2 +json+native+treesitter%gcc@") == {}
    assert parse_alloc_spec("emacs@29.2 +json+native+treesitter%gcc") == {}

    # missing package version
    assert parse_alloc_spec("emacs@ +json+native+treesitter%gcc@12.3.0") == {}
    assert parse_alloc_spec("emacs+json+native+treesitter%gcc@12.3.0") == {}

    # invalid variants
    assert parse_alloc_spec("emacs@29.2 this_is_not_a_thing%gcc@12.3.0") == {}
