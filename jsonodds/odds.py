from .api import API


class Odds(API):
    def __int__(self, api_key, timeout=5, sleep_time=1.5):
        super().__init__(api_key, timeout, sleep_time)

    def get_odds(self, sport=None, odd_type=None, odd_format=None):
        """" Get list of games and odds for every quarter """
        if sport is not None:
            path = "odds/{sport}".format(sport=sport)
        else:
            path = "odds/"
        if odd_format is not None and odd_type is not None:
            path += "?oddFormat={}&oddType={}".format(odd_format, odd_type)
        elif odd_format is not None:
            path += "?oddFormat={}".format(odd_format)
        elif odd_type is not None:
            path += "?oddType={}".format(odd_type)
        return self._make_request(path)
