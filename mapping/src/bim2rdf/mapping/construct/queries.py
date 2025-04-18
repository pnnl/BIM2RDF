
from bim2rdf.core.queries import SPARQLQuery as Query    
from . import included_dir
included = tuple(Query.s([included_dir]))
