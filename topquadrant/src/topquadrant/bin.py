
from .install import ShaclInstallation
_ = ShaclInstallation()
from platform import platform
ext = '.bat' if 'win' in platform().lower() else '.sh'
validate = _.bin / ('shaclvalidate'+ext)
infer = _.bin / ('shaclinfer'+ext)

