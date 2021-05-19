import json
from urllib.parse import urljoin

import requests

from . import settings


class BaseAPIClient:
    
    def __init__(
                self,
                endpoint=None,
                url=settings.BASE_URL,
    ):
        self.endpoint = endpoint
        self.url = url
        self.headers = {
            
        }
    
    def _get_json_response(self, url: str, params=None):
        response = requests.get(url=url, headers=self.headers, params=params)
        return json.loads(response.content)

    def list_url(self):
        return urljoin(self.url, self.endpoint)

    def detail_url(self, identifier: int):
        return urljoin(self.list_url(), str(identifier))

    def get_list(self, params=None):
        url = self.list_url()
        return self._get_json_response(url=url, params=params)

    def get_item(self, identifier: int, params=None):
        url = self.detail_url(identifier=identifier)
        return self._get_json_response(url=url, params=params)
