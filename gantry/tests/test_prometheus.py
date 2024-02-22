import pytest

from gantry.clients.prometheus import util
from gantry.clients.prometheus.prometheus import PrometheusClient
from gantry.tests.defs.prometheus import (
    ENCODED_QUERY_DICT,
    ENCODED_QUERY_STR,
    INVALID_QUERY,
    QUERY_DICT,
    QUERY_STR,
)


def test_cookie_set():
    """Test that a cookie is set when specified"""
    p = PrometheusClient("", "cookie")
    assert p.cookies == {"_oauth2_proxy": "cookie"}


def test_process_query():
    """Test that a query is parsed and encoded properly, from both dict and string"""
    assert util.process_query(QUERY_DICT) == ENCODED_QUERY_DICT
    assert util.process_query(QUERY_STR) == ENCODED_QUERY_STR
    with pytest.raises(ValueError):
        util.process_query(INVALID_QUERY)
