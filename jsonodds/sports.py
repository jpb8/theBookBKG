from .api import API


class Sports(API):
    def __int__(self, api_key, timeout=5, sleep_time=1.5):
        super().__init__(api_key, timeout, sleep_time)

    def get_sports(self):
        """" Get list of games and odds for every quarter """
        path = "sports"
        return self._make_request(path)