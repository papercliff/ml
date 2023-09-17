import json
import unittest

import wsgi


class TestWSGI(unittest.TestCase):
    data = json.dumps({'text': 'Kevin McCarthy: House impeachment inquiry into Biden is a ‘natural step forward’'})
    client = wsgi.app.test_client()

    def test_keywords(self):
        response = self.client.post(
            "/keywords",
            data=self.data,
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data),
            [
                ['impeachment', 0.5347],
                ['mccarthy', 0.437],
                ['biden', 0.408],
                ['step', 0.2471],
                ['inquiry', 0.2396],
                ['kevin', 0.2251],
                ['forward', 0.2141],
                ['house', 0.1815],
                ['natural', 0.14]
            ]
        )

    def test_not_found(self):
        response = self.client.post(
            "/random",
            data=self.data,
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
