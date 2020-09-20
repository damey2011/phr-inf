import json
import re
import unittest

from app import app


class TestApp(unittest.TestCase):
    def setUp(self) -> None:
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.client.environ_base['Content-Type'] = 'application/json'
        self.end_point = '/api/sentence-gen/'

    def test_that_empty_words_not_allowed(self) -> None:
        response = self.client.post(self.end_point, data=json.dumps({'word': ''}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get('message'), 'Please provide a valid word.')

    def test_that_null_value_word_is_not_allowed(self) -> None:
        response = self.client.post(self.end_point, data=json.dumps({'word': None}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get('message'), 'Please provide a valid word.')

    def test_that_endpoint_rejects_non_string_input(self) -> None:
        response = self.client.post(self.end_point, data=json.dumps({'word': {'text': 'some randdom'}}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get('message'), 'Please provide a valid word.')

    def test_palindrome(self) -> None:
        p_word = 'hannah'
        response = self.client.post(self.end_point, data=json.dumps({'word': p_word}))
        self.assertEqual(response.status_code, 200)
        pattern = re.compile(r"^[\w+. ]* is a palindrome$")
        self.assertRegex(response.json.get('message'), pattern)

    def test_not_palindrome(self) -> None:
        p_word = 'hippopotamus'
        response = self.client.post(self.end_point, data=json.dumps({'word': p_word}))
        self.assertEqual(response.status_code, 200)
        pattern = re.compile(r"^[\w+. ]* is not a palindrome$")
        self.assertRegex(response.json.get('message'), pattern)

    def test_random_number_range(self) -> None:
        p_word = 'hippopotamus'
        # lets run this 20 times, not quite efficient, but so it generates the number at least 20 times
        for i in range(20):
            response = self.client.post(self.end_point, data=json.dumps({'word': p_word}))
            self.assertEqual(response.status_code, 200)
            pattern = re.compile(r"^I would like ([1-9]|10) [\w+. ]*$")
            self.assertRegex(response.json.get('message'), pattern)

    def test_that_palindrome_message_semantic_is_correct(self) -> None:
        p_word = 'hannah'
        response = self.client.post(self.end_point, data=json.dumps({'word': p_word}))
        self.assertEqual(response.status_code, 200)
        pattern = re.compile(
            r'^I would like ([1-9]|10) ' + p_word + ' please[.] ' + p_word.capitalize() + ' is a palindrome$'
        )
        self.assertRegex(response.json.get('message'), pattern)

    def test_that_non_palindrome_message_semantic_is_correct(self) -> None:
        p_word = 'hippopotamus'
        response = self.client.post(self.end_point, data=json.dumps({'word': p_word}))
        self.assertEqual(response.status_code, 200)
        pattern = re.compile(
            r'^I would like ([1-9]|10) ' + p_word + ' please[.] ' + p_word.capitalize() + ' is not a palindrome$'
        )
        self.assertRegex(response.json.get('message'), pattern)


if __name__ == '__main__':
    unittest.main()
