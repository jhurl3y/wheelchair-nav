import navigation as nav
import gps_obj as gps

loc_a = gps.GPS(53.272909, -9.059584)
loc_b = gps.GPS(53.273292, -9.060419)
print(nav.get_bearing(loc_a, loc_b))
print(nav.get_distance(loc_a, loc_b))
# 53.272909, -9.059584 google maps home
# 53.272725, -9.059466667 home
# 53.275225, -9.057401 cath
# 53.273292, -9.060419 st josephs
 
