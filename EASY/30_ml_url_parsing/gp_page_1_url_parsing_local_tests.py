"""Local regression tests for the URL parsing solution."""

import unittest
from unittest.mock import Mock, patch

import requests

from gp_page_1_url_parsing_solution import normalize_url, parse_urls


class UrlParsingTests(unittest.TestCase):
    """Check public behavior without making real network requests."""

    def test_normalize_url_preserves_path_case(self) -> None:
        """Only the host should be lowercased."""
        self.assertEqual(
            normalize_url("EN.WIKIPEDIA.ORG/wiki/Special:Random"),
            "en.wikipedia.org/wiki/Special:Random",
        )

    def test_normalize_url_removes_trailing_characters(self) -> None:
        """Sentence punctuation and a final slash should be removed."""
        self.assertEqual(normalize_url("Example.COM/"), "example.com")
        self.assertEqual(
            normalize_url("Example.COM/Path,)."),
            "example.com/Path",
        )

    @patch("gp_page_1_url_parsing_solution.requests.get")
    def test_original_example(self, mock_get: Mock) -> None:
        """The example from the task should be parsed correctly."""
        response = Mock()
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        message = (
            "Check out this link www.example.com, example.com and"
            " also https://www.xn--80ak6aa92e.com/"
            " also www.xn--80ak6aa92e.com"
            " also xn--80ak6aa92e.com"
            " also apple.com"
            " Don't miss this great opportunity!"
            " www.google.com."
        )

        self.assertEqual(
            parse_urls(message),
            {
                "example.com": 2,
                "xn--80ak6aa92e.com": 3,
                "apple.com": 1,
                "google.com": 1,
            },
        )

    @patch("gp_page_1_url_parsing_solution.requests.get")
    def test_stackoverflow_path_is_preserved(self, mock_get: Mock) -> None:
        """Regression test for the first hidden platform failure."""
        response = Mock()
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        message = (
            "https://stackoverflow.com/questions/tagged/python "
            "has answers to many Python questions."
        )

        self.assertEqual(
            parse_urls(message),
            {"stackoverflow.com/questions/tagged/python": 1},
        )

    @patch("gp_page_1_url_parsing_solution.requests.get")
    def test_wikipedia_path_case_is_preserved(self, mock_get: Mock) -> None:
        """Regression test for the second hidden platform failure."""
        response = Mock()
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        message = (
            "Explore https://en.wikipedia.org/wiki/Special:Random "
            "for a random Wikipedia article."
        )

        self.assertEqual(
            parse_urls(message),
            {"en.wikipedia.org/wiki/Special:Random": 1},
        )

    @patch("gp_page_1_url_parsing_solution.requests.get")
    def test_duplicate_urls_make_one_request(self, mock_get: Mock) -> None:
        """Repeated forms should be counted but fetched only once."""
        response = Mock()
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        result = parse_urls(
            "example.com www.example.com https://www.example.com/"
        )

        self.assertEqual(result, {"example.com": 3})
        mock_get.assert_called_once_with("http://example.com", timeout=5)

    @patch("gp_page_1_url_parsing_solution.requests.get")
    def test_unreachable_url_is_excluded(self, mock_get: Mock) -> None:
        """A RequestException should remove only the failing URL."""
        good_response = Mock()
        good_response.raise_for_status.return_value = None

        def request_side_effect(url: str, timeout: int) -> Mock:
            self.assertEqual(timeout, 5)
            if url == "http://broken.test":
                raise requests.RequestException("unreachable")
            return good_response

        mock_get.side_effect = request_side_effect

        result = parse_urls("example.com broken.test example.com")

        self.assertEqual(result, {"example.com": 2})
        self.assertEqual(mock_get.call_count, 2)

    @patch("gp_page_1_url_parsing_solution.requests.get")
    def test_empty_message(self, mock_get: Mock) -> None:
        """An empty message should return an empty dictionary."""
        self.assertEqual(parse_urls(""), {})
        mock_get.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
