from .base import BaseAPIClient


class PeopleAPIClient(BaseAPIClient):
    def __init__(self, api_key=None):
        super().__init__(endpoint='people/')

    def get_people(self, params=None):
        return self.get_list(params=params)


class PlanetsAPIClient(BaseAPIClient):
    def __init__(self, api_key=None):
        super().__init__(endpoint='planets/')
