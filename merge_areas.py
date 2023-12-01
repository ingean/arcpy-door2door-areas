import os
import arcpy
from modules.log import Log
from modules.arcgis.dataset import export_dataset, count_rows, get_min_row

log = Log(arcgis=True)
arcpy.env.overwriteOutput = True

SOURCE_GDB = r'D:\Data\Kreftforeningen_roder\namsos.gdb'
AREAS = os.path.join(SOURCE_GDB, 'roder_krk_bruksenheter_split_single_statistics')
MERGED_AREAS = os.path.join(SOURCE_GDB, 'roder_krk_bruksenheter_split_single_merge')

# Script inputs
#AREAS = arcpy.GetParameter(0) # Areas to merge
#MERGED_AREAS = arcpy.GetParameter(1)

ABS_MIN_COUNT = 5
MIN_COUNT = 20
MAX_COUNT = 50
MAX_TIME = 60
MAX_LENGTH = 3

def get_adjacent_polygons(areas_fc, oid):
  log.info(f" - Finner naboer til rode med objektid: {oid}...")
  selected_area = arcpy.management.SelectLayerByAttribute(
    areas_fc, 
    "NEW_SELECTION", 
    f"OBJECTID = {oid}"
  )
    
  result1 = arcpy.management.SelectLayerByLocation(
    selected_area, 
    "SHARE_A_LINE_SEGMENT_WITH", 
    selected_area, 
    None, "NEW_SELECTION"
  )

  result = arcpy.management.SelectLayerByAttribute(
    selected_area, 
    "REMOVE_FROM_SELECTION", 
    f"OBJECTID = {oid}"
  )

  count = count_rows(result[0])
  log.info(f' - Roden har {count} naboer')
  return result[0]

def merge_areas(poly_fc):
  log.info(f"Prøver å slå sammen roder med færre enn {MIN_COUNT} boenheter med et tilstøtende område...")
 
  areas = r'memory/single_areas'
  export_dataset(poly_fc, areas)
  has_matches = False

  fields = ["OBJECTID", "AreaID", "Join_Count", "Total_traveltime", "Total_travellength"]
  
  with arcpy.da.UpdateCursor(areas, fields, where_clause=f"Join_Count <= {MIN_COUNT}") as cursor:
    for row in cursor:
      
      log.info(f"Rode med objektid {row[0]} har {row[2]} boenheter og {round(row[3], 1)} min reisetid...")
      adjacent_areas = get_adjacent_polygons(areas, row[0])

      merge_id = ''
      lowest_count_row = get_min_row(adjacent_areas, fields, "Join_Count")
      shortest_time_row = get_min_row(adjacent_areas, fields, "Total_traveltime")

      if (row[2] + lowest_count_row[2]) <  MAX_COUNT and (row[3] + lowest_count_row[3]) < MAX_TIME:
        log.info(f" - Slår sammen med naborode med objektid {lowest_count_row[0]} som har færrest boenheter")
        merge_id = lowest_count_row[1]
      elif (row[2] + shortest_time_row[2]) <  MAX_COUNT and (row[3] + shortest_time_row[3]) < MAX_TIME:
        log.info(f" - Slår sammen med naborode med objektid {shortest_time_row[0]} som har kortest reisetid")
        merge_id = shortest_time_row[1]
      elif row[2] < ABS_MIN_COUNT:
        log.info(f" - Slår sammen med naborode med objektid {lowest_count_row[0]} da roden har færre enn {ABS_MIN_COUNT} boenheter")
        merge_id = lowest_count_row[1]

      if merge_id != '':
        has_matches = True
        row[1]  = merge_id
        cursor.updateRow(row)
      else:
        log.info(f'Fant ingen naboer som rode med objektid {row[1]} kan slås sammen med uten at antall boenheter overskrider {MAX_COUNT} boenheter og/eller {MAX_TIME} min gangtid')
    
  if has_matches:
    log.info(f'Slår sammen roder med lik AreaID...')
    arcpy.management.Dissolve(areas, MERGED_AREAS, "AreaID", None, "SINGLE_PART", "DISSOLVE_LINES", '')
  else:
    log.info(f"Ingen roder med få boenheter kunne slås sammen med naboroder!")

###############################################################################
merge_areas(AREAS)
