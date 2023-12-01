"""
For a set of areas (e.g. sales districts) calculate the total walk time to visit
a set of destinations (e.g. boenheter) within each area. 

The goal is to evaluate if the walktime for each area is balanced (approximately)
the same. 
"""

import arcpy
from modules.arcgis.dataset import add_fields, count_rows
from modules.arcgis.na.routing import create_route_analysis, load_and_solve_route, get_routes_cursor
from modules.log import Log

log = Log()

result_fields = [
  ['Stops_count', 'LONG'],
  ['Total_traveltime', 'DOUBLE'],
  ['Total_travellength', 'DOUBLE']
]

def get_stops(area, areas_fc, destinations_fc):
  selected_area_layer = arcpy.management.SelectLayerByAttribute(
    areas_fc, 
    "NEW_SELECTION", 
    f"OBJECTID = {area[0]}"
  )
    
  result = arcpy.management.SelectLayerByLocation(
    destinations_fc, 
    "INTERSECT", 
    selected_area_layer, 
    None, "NEW_SELECTION"
  )
  count = count_rows(result[0])
  log.info(f'OBJECTID: {area[0]} has {count} stops')
  return [result[0], count]

def get_results(result):
  wt = 0
  wl = 0
  routes = get_routes_cursor(result)
  if routes is not None:
    for route in routes:
      wt += route[0]
      wl += route[1]
 
  log.info(f'Route has a total walktime of {wt} mins ({wl} km)')
  return [wt,wl]

def calculate_traveltime_pr_area(points_fc, areas_fc, travel_mode):
  add_fields(areas_fc, result_fields)

  # Instantiate a Route analysis object.
  options = {
    'travelMode': travel_mode,
    'findBestSequence': True
  }
  routing = create_route_analysis(options) # Defaults to using ELVEG

  fields = ["OBJECTID"] + [field[0] for field in result_fields]
 
  with arcpy.da.UpdateCursor(areas_fc, fields) as areas_cursor:
    for area in areas_cursor:  
      stops = get_stops(area, areas_fc, points_fc)
    
      result = load_and_solve_route(routing, stops[0])
      r = get_results(result)
      area[1] = stops[1]
      area[2] = r[0]
      area[3] = r[1]
      areas_cursor.updateRow(area)


   






