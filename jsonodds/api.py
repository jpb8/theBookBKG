import requests
import time


class API(object):
    """JsonOdds API"""

    # Create a persistent requests connection
    session = requests.Session()
    session.headers = {'application': 'PythonWrapper'}

    def __init__(self, api_key, timeout=5, sleep_time=1.5):
        """ JsonODDS API Constructor
        :param api_key: key provided by Sportradar, specific to the sport's API
        :param timeout: time before quitting on response (seconds)
        :param sleep_time: time to wait between requests, (free min is 1 second)
        """

        assert api_key != '', 'Must supply a non-empty API key.'
        self.api_key = {'x-api-key': api_key}
        self.api_root = 'https://jsonodds.com/api/'
        self.timeout = timeout
        self._sleep_time = sleep_time

    def _make_request(self, path, method='GET'):
        """Make a GET or POST request to the API"""
        time.sleep(self._sleep_time)  # Rate limiting
        full_uri = self.api_root + path
        response = self.session.request(method,
                                        full_uri,
                                        timeout=self.timeout,
                                        headers=self.api_key)
        # response.raise_for_status()  # Raise error for bad status
        return response