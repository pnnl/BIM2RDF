#Problem: mapping files that dont have a .mapping extention are being picked up. 
#Test file to print which files get picked up.
#Results: before files such as "mapping/s223/space-lightconnector.rq" were being picked up
#After fixing the speckle.py file entries like the above without the .mapping are not picked up.

import mapping.speckle as sp
from mapping import mapping_dir
from icecream import ic

maps_dir = mapping_dir / 's223'

var = sp.maps(maps_dir=maps_dir)
ic(var)
