import pytest
from utility.utils import get_matches

class TestUtils:
    def test_get_matches_exact_match(self):
        choices = ["apple", "banana", "cherry"]
        matches = get_matches("apple", choices)
        assert len(matches) > 0
        assert matches[0][0] == "apple"
        assert matches[0][1] == 100

    def test_get_matches_partial_match(self):
        choices = ["apple", "application", "apply"]
        matches = get_matches("app", choices)
        assert len(matches) > 0
        assert all(match[1] > 0 for match in matches)

    def test_get_matches_empty_query(self):
        choices = ["apple", "banana", "cherry"]
        matches = get_matches("", choices)
        assert len(matches) <= 5
        assert all(match[1] == 0 for match in matches)

    def test_get_matches_limit(self):
        choices = ["apple", "banana", "cherry", "date", "elderberry"]
        matches = get_matches("e", choices, limit=3)
        assert len(matches) <= 3
