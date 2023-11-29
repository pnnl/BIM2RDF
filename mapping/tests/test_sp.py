#Test 1

#Problem: mapping files that dont have a .mapping extention are being picked up. 
#Test file to print which files get picked up.
#Results: before files such as "mapping/s223/space-lightconnector.rq" were being picked up
#After fixing the speckle.py file entries like the above without the .mapping are not picked up.

import mapping.speckle as spek
#from mapping import mapping_dir
from icecream import ic

#maps_dir = mapping_dir / 's223'

#var = spek.maps(maps_dir=maps_dir)
#ic(var)
    
#~~~~~~~~~~~~~~~
################
#~~~~~~~~~~~~~~~
#Test 2 
#Problem: when doing the mapping branch_ids are not accepted when input as a set
#Test that feeds branch_ids as a set to the engine func. 
#Result: before fix if the branch_ids were given as a set a TypeError is raised
#after fix if a set is fed in the mapping proceedes as normal


branch_id = {'electrical/panels'} #Set
stream_id = "Pritoni"

var = spek.engine(stream_id, branch_ids=branch_id)
ic(var)

