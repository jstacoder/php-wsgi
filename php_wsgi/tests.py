from werkzeug.test import Client
from php_app import PhpWsgiApp


def test():
	app = PhpWsgiApp()
	client = app.app.test_client()

	res = client.get('/?name=hank')

	assert 'hank' in res.data

if __name__ == '__main__':
    test()
