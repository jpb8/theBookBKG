from .api import API


class Results(API):
    def __int__(self, api_key, timeout=5, sleep_time=1.5):
        super().__init__(api_key, timeout, sleep_time)

    def get_results(self, sport=None, final=None, type=None):
        """" Get list of results for a given sport """
        if sport is not None:
            path = "results/{sport}".format(sport=sport)
        else:
            path = "odds/"
        if final is not None and type is not None:
            path += "?oddFormat={}&oddType={}".format(final, type)
        elif final is not None:
            path += "?oddFormat={}".format(final)
        elif type is not None:
            path += "?oddType={}".format(type)
        return self._make_request(path)