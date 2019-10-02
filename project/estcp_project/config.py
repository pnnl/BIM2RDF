import yaml
from estcp_project import root
#_ = here('./config.yaml')
#_ = open(_)
#_ = yaml.safe_load(_)
#config = _
#del _

_secrets_file = root / 'secrets.yaml'
if _secrets_file.exists():
    secrets = yaml.safe_load(open(_secrets_file))
else:
    secrets = {}


def save_secrets(get_secrets):
    secrets = get_secrets()
    yaml.dump(secrets, open(_secrets_file, 'w'))
