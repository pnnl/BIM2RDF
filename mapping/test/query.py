q = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

# 'overall' check for shacl
select (?checks = ?count  as ?this) {

# 'check' level
#        using if b/c apparently ops on boolean dont see it as numeric
select   ( sum(if(?loc_lpd < 100, 1, 0)) as ?checks)  (count(?loc_lpd) as ?count)     {

# 'lower-level': agg. by room
    select ?loc_type  ?loc ?area  (sum(?power/?area) as ?loc_lpd)  (sum(?power) as ?loc_power )     { 
    ?luminaire a brick:Luminaire. 
    ?luminaire brick:hasLocation ?loc. 
    ?luminaire brick:hasLocation/a ?loc_type. 
    ?loc_type rdfs:subClassOf brick:Room. # in owl is room a subclass of itself?? 
    #?loc_type sesame:directSubClassOf brick:Room. # elimnates 'synonyms' and going up the heirarchy 
    ?luminaire brick:ratedPowerInput/brick:value ?power.
    ?loc brick:grossArea/brick:value ?area. 
    #?loc a brick:Mechanical_Room. # testing filter
    } group by ?loc_type ?loc ?area
 
  }

}

"""


import sys
import rdflib
_ = rdflib.Graph()
_.parse(sys.argv[1])
_ = _.query(q)
_ = list(_)
for __ in _: print(*(map(lambda _:_.toPython(), __)),   sep='\t')

