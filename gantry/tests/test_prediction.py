import pytest

from gantry.routes.prediction import prediction
from gantry.tests.defs import prediction as defs
from gantry.util.prediction import validate_payload


@pytest.fixture
async def db_conn_inserted(db_conn):
    """Returns a connection to a database with 5 samples inserted"""

    with open("gantry/tests/sql/insert_samples.sql") as f:
        await db_conn.executescript(f.read())

    return db_conn


async def test_exact_match(db_conn_inserted):
    """All fields are an exact match for 5 samples in the database."""

    assert (
        await prediction.predict_single(db_conn_inserted, defs.NORMAL_BUILD)
        == defs.NORMAL_PREDICTION
    )


async def test_expensive_variants(db_conn_inserted):
    """
    Tests whether the algorithm filters by expensive variants.
    The input has been modified to prevent an exact match with
    any of the samples.
    """

    assert (
        await prediction.predict_single(db_conn_inserted, defs.EXPENSIVE_VARIANT_BUILD)
        == defs.NORMAL_PREDICTION
    )


async def test_no_variant_match(db_conn_inserted):
    """
    All fields match except for variants, expect default predictions with no sample.
    """

    assert (
        await prediction.predict_single(db_conn_inserted, defs.BAD_VARIANT_BUILD)
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
    diff_compiler_build["compiler"]["name"] = "gcc-different"

    assert (
        await prediction.predict_single(db_conn_inserted, diff_compiler_build)
        == defs.NORMAL_PREDICTION
    )


async def test_empty_sample(db_conn):
    """No samples in the database, so we expect default predictions."""

    assert (
        await prediction.predict_single(db_conn, defs.NORMAL_BUILD)
        == defs.DEFAULT_PREDICTION
    )


# Test validate_payload


def test_valid_payload():
    """Tests that a valid payload returns True"""
    assert validate_payload(defs.NORMAL_BUILD) is True


def test_invalid_payloads():
    """Test a series of invalid payloads"""

    # non dict
    assert validate_payload("hi") is False

    build = defs.NORMAL_BUILD.copy()
    # missing package
    del build["package"]
    assert validate_payload(build) is False

    build = defs.NORMAL_BUILD.copy()
    # missing compiler
    del build["compiler"]
    assert validate_payload(build) is False

    # name and version are strings in the package and compiler
    for key in ["name", "version"]:
        for field in ["package", "compiler"]:
            build = defs.NORMAL_BUILD.copy()
            build[field][key] = 123
            assert validate_payload(build) is False

    # invalid variants
    build = defs.NORMAL_BUILD.copy()
    build["package"]["variants"] = "+++++"
    assert validate_payload(build) is False
