import requests
from django.test import TestCase
from mock import patch

from quis.views import get_watchman_data


@patch('quis.views.session.get')
class FetchAndFormatTests(TestCase):
    URL_IS_IGNORED_BECAUSE_MOCK = 'https://url.is.ignored/because/mock/'
    POSITIVE_TEST_CASES = [
        # (get_response, expected_result)
        ({'storage': {'ok': True}},
         [{'name': 'storage', 'ok': True, 'details': {}}]),
        ({'databases': [{'default': {'ok': True}},
                        {'notdefault': {'ok': True}}]},
         [{'name': 'databases/default', 'ok': True, 'details': {}},
          {'name': 'databases/notdefault', 'ok': True, 'details': {}}]),
        ({'cache': [{'default': {'ok': True}},
                    {'shared': {'ok': False, 'error': 'it broke'}}]},
         [{'name': 'cache/default', 'ok': True, 'details': {}},
          {'name': 'cache/shared', 'ok': False,
           'details': {'error': 'it broke'}}]),
        ({'deploy': {'ok': True, 'git hash': 'abcdef', 'branch': 'develop'}},
         [{'name': 'deploy', 'ok': True,
           'details': {'git hash': 'abcdef', 'branch': 'develop'}}]),
    ]

    def test_get_watchman_data(self, mock_get):
        for get_response, expected_result in self.POSITIVE_TEST_CASES:
            mock_get.return_value.json.return_value = get_response
            result = get_watchman_data(self.URL_IS_IGNORED_BECAUSE_MOCK)
            self.assertEqual(result, expected_result)

    def test_get_watchman_data_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError
        result = get_watchman_data(self.URL_IS_IGNORED_BECAUSE_MOCK)
        self.assertEqual(result, [])
