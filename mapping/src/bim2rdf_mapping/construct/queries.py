
from bim2rdf.queries import SPARQLQuery as Query    
from . import default_dir
default = tuple(Query.s([default_dir]))
