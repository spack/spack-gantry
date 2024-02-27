import pytest

from gantry.clients.prometheus import util
from gantry.clients.prometheus.prometheus import PrometheusClient
from gantry.tests.defs import prometheus as defs


def test_cookie_set():
    """Test that a cookie is set when specified"""
    p = PrometheusClient("", "cookie")
    assert p.cookies == {"_oauth2_proxy": "cookie"}


def test_process_query():
    """Test that a query is parsed and encoded properly, from both dict and string"""
    assert util.process_query(defs.QUERY_DICT) == defs.ENCODED_QUERY_DICT
    assert util.process_query(defs.QUERY_STR) == defs.ENCODED_QUERY_STR
    with pytest.raises(ValueError):
        util.process_query(defs.INVALID_QUERY)
