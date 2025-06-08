# Create your tests here.

import requests

test_response = requests.request(method='get', url='http://127.0.0.1:8000/api/test', params={'colors': ['red', 'green', 'blue']})
print(test_response)

