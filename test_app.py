import unittest
from app import app

class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_page_and_assets(self):
        page = self.client.get('/')
        self.assertEqual(page.status_code, 200)
        self.assertIn(b'Dashboard Overview', page.data)
        self.assertNotIn(b'```', page.data)
        for url in ['/static/script.js', '/static/style.css']:
            with self.client.get(url) as response:
                self.assertEqual(response.status_code, 200)

    def test_invalid_payloads(self):
        for payload in [None, [], 'text', {}, {'message': None}, {'message': 3}, {'message': []}, {'message': '  '}, {'message': 'a' * 10001}]:
            with self.subTest(payload=str(payload)[:40]):
                response = self.client.post('/predict', json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.json)
        self.assertEqual(self.client.post('/predict', data='{', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/predict', data='a' * 70000, content_type='application/json').status_code, 413)

    def test_predictions_and_evidence(self):
        for message, expected in [('Hi, are we still meeting for lunch at noon?', 'NOT SPAM'), ('Congratulations! You have won a free cash prize. Call now to claim your reward!', 'SPAM')]:
            result = self.client.post('/predict', json={'message': message})
            self.assertEqual(result.status_code, 200)
            data = result.json
            self.assertEqual(data['result'], expected)
            self.assertAlmostEqual(data['spam_probability'] + data['not_spam_probability'], 100, places=1)
            self.assertTrue(all(word in message.lower() for word in data['keywords']))
            self.assertEqual(data['category'], 'Scams' if expected == 'SPAM' else None)

    def test_evaluation(self):
        data = self.client.get('/metrics').json
        self.assertEqual(sum(map(sum, data['confusion_matrix'])), data['test_size'])
        self.assertGreater(data['accuracy'], 90)
        self.assertGreaterEqual(data['auc'], 0)
        self.assertLessEqual(data['auc'], 1)
        self.assertEqual(data['roc'][0], [0, 0])
        self.assertEqual(data['roc'][-1], [1, 1])

if __name__ == '__main__':
    unittest.main()
