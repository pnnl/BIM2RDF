
from bim2rdf.queries import SPARQLQuery as Query    
from . import included_dir
included = tuple(Query.s([included_dir]))
