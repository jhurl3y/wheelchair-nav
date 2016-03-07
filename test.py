import gps_navigator 
import gps_obj as gps

loc_a = gps.GPS(53.272725, -9.059466667)# home
loc_b = gps.GPS(53.273292, -9.060419)# st josephs

#loc_b = gps.GPS(43.682213, -70.450696)
#loc_a = gps.GPS(43.682194, -70.450769)

nav = gps_navigator.NAVIGATOR()
nav.go(loc_a, loc_b)
# # print(nav.get_bearing(loc_a, loc_b))
# # print(nav.get_distance(loc_a, loc_b))
# print(nav.convert_from_degrees(70.450769123428)) # 70.450769
#print(nav.convert_to_degrees(70, 27, 2.7684))

# 53.272909, -9.059584 google maps home
# 53.272725, -9.059466667 home
# 53.275225, -9.057401 cath
# 53.273292, -9.060419 st josephs
 
