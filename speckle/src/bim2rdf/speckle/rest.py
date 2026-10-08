# https://github.com/specklesystems/specklepy/blob/main/src/specklepy/bundle/download.py#L43
from bim2rdf.core.config import config
url = f'https://{config.speckle.server}/api/v2'


class urls:
    base = url
    @classmethod
    def artifacts(cls, *, project_id, model_id, version_id):
        _ = f"{cls.base}/projects/{project_id}/models/{model_id}/versions/{version_id}/artifacts"
        return _


from .requests import TokenAuth
import requests

from bim2rdf.cache import cache
@cache
def artifacts(*, project_id, model_id, version_id) -> dict:
    _ = urls.artifacts(project_id=project_id, model_id=model_id, version_id=version_id)
    _ = requests.get(_, headers = {"Accept": "application/json" },  auth=TokenAuth(),)
    _ = _.json()
    return _
