import pytest
from zip_sync.filter.zip_code_filter import is_max_call_price_above_threshold, filter_zip_codes

@pytest.mark.parametrize("entry,threshold,expected", [
    ({'max_call_price': 25}, 20, True),
    ({'max_call_price': 20}, 20, False),
    ({'max_call_price': 19.99}, 20, False),
    ({'max_call_price': '30'}, 20, True),
    ({'max_call_price': 'not_a_number'}, 20, False),
    ({'max_call_price': None}, 20, False),
    ({}, 20, False),
])
def test_is_max_call_price_above_threshold(entry, threshold, expected):
    assert is_max_call_price_above_threshold(entry, threshold) == expected

def test_filter_zip_codes():
    data = [
        {'zip_code': '12345', 'max_call_price': 25},
        {'zip_code': '23456', 'max_call_price': 15},
        {'zip_code': '34567', 'max_call_price': 'not_a_number'},
        {'zip_code': '45678', 'max_call_price': 21},
    ]
    assert filter_zip_codes(data) == ['12345', '45678'] 