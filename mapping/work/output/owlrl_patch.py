# -*- coding: utf-8 -*-


# patching owlrl-script.py to fix 
# maybe use owlready. or just its reasoner
# or ontop reasoner?
# TODO: check periodically if this issue has been resolved

# https://github.com/RDFLib/OWL-RL/issues/53
from rdflib import OWL, RDFS
OWL.Datatype = RDFS.Datatype



#https://github.com/RDFLib/OWL-RL/issues/57
import rdflib
class _Graph(rdflib.Graph):
    def serialize(self, *p, **k):
        _ = super().serialize(*p, **k)
        if isinstance(_, str):
            _ = _.encode('utf-8')
        return _
rdflib.Graph = _Graph


import re
import sys

from owlrl._cli import main


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
    #_ = '\u03bc'.encode('utf-8')
    #print(_)
