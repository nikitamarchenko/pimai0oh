__author__ = 'nmarchenko'

import unittest


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        from pimai0oh import app
        self.app = app.test_client()

    def tearDown(self):
        pass

    def login(self, username, password):
        return self.app.post('/', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login(self):
        rv = self.login('koko', 'vkoynaktest')
        assert 'No entries here so far' in rv.data
