"""
Calculate a travel time index for each point in a feature class. 

The travel time index is the mean travel time to the x closest
neighbors (using the road network) for each point. A high index indicates a point which is
off the beaten path e.g. far from its neigbors.  
"""
import arcpy
from modules.log import Log
from modules.arcgis.na.odmatrix import create_origin_destination_analysis, load_and_solve_od_matrix, get_od_lines 
from modules.arcgis.dataset import featureclass_to_dict, add_fields
log = Log()

# Input parameters
options = {
  'travelMode': 'Gange',
  'defaultImpedanceCutoff' : 15
}

result_fields = [
  ['Weight', 'DOUBLE'],
  ['WeightCount','LONG']
]

min_travel_length = 10 # Used as travel length for overlapping points e.g. apartments in same building.

def calculate_traveltime_weight(points_fc: str, number_of_neighbors) -> None:
  add_fields(points_fc, result_fields)
  od_matrix = create_origin_destination_analysis(options)
  od_matrix.defaultDestinationCount = number_of_neighbors
  result = load_and_solve_od_matrix(od_matrix, points_fc, points_fc)
  get_od_lines(result, r'memory\ODLines')

  fields = arcpy.ListFields(r'memory\ODLines')
  
  log.info(f'Converting OD matrix to lookup dictionary...')
  od_matrix_dict = featureclass_to_dict(r'memory\ODLines', ["OID@", "OriginOID","Total_Distance", "SHAPE@LENGTH"])

  log.info(f'Starting to update {points_fc}...')
  with arcpy.da.UpdateCursor(points_fc, ["OBJECTID", "Weight", "WeightCount"]) as update_cursor:
    for feature in update_cursor:
      feature_traveltimes = {k: v for k, v in od_matrix_dict.items() if v[0] == feature[0]} # Get walk times for the current feature
      travel_weight_count = 0
      travel_weight = 0
      
      for row in feature_traveltimes.items():
        travel_weight_count += 1
        travel_length = row[1][1] if row[1][1] > 0 else min_travel_length # If points are stacked and have zero in walking distance
        travel_length = row[1][2] if travel_length < (row[1][2]/1000) else travel_length # Use shape length if longer than travel length
        travel_weight += travel_length

      travel_weight = travel_weight / travel_weight_count
      feature[1] = travel_weight
      feature[2] = travel_weight_count
      update_cursor.updateRow(feature)

  log.info(f'Finished adding travel weights to {points_fc}!')