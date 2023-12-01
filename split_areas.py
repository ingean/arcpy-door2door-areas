import arcpy
from modules.log import Log
from modules.utils import create_uuid
from modules.arcgis.dataset import export_dataset, add_field
from modules.arcgis.na.location_allocation import create_location_allocation_analysis, load_and_solve_location_allocation, get_la_demand_points

log = Log(arcgis=True)
arcpy.env.overwriteOutput = True

MAX_COUNT = 70
TARGET_COUNT = 40

LA_OPTIONS = {
  'travelMode': 'Gange',
  'defaultImpedanceCutoff': 15,
  'problemType': arcpy.nax.LocationAllocationProblemType.MinimizeImpedance,
  'timeUnits': arcpy.nax.TimeUnits.Minutes
}

def summarize_by_area(areas, id_field):
  log.info(f'Teller opp antall bruksenheter i hver rode...')
  stats_table = r'memory/areas_stats'
  arcpy.analysis.Statistics(areas, stats_table, [["OBJECTID", "COUNT"]], id_field)
  return stats_table

def split_area(la_analysis, points_fc, fid, count):
  areas_to_find = round(count/TARGET_COUNT)
  log.info(f'Splitter rode {fid} i {areas_to_find} deler...')
  demand_points = r'memory/demand_points'
  export_dataset(points_fc, demand_points, f"FacilityOID = {fid}")

  facilities = r'memory/facilities'
  export_dataset(demand_points, facilities)
  arcpy.management.DeleteIdentical(facilities, ['SHAPE'])

  la_analysis.facilityCount = areas_to_find 
  result = load_and_solve_location_allocation(la_analysis, facilities, demand_points)

  result_points = r'memory/result_points'
  get_la_demand_points(result, result_points)
  return result_points

def update_points(points_fc, result_points, area_id):
  log.info(f'Oppdaterer punkter for rode {area_id}...')
 
  export_dataset(points_fc, r'memory/results_erase', f"AreaID <> '{area_id}'")
  arcpy.management.Merge([r'memory/results_erase', result_points], 
                       points_fc, "", "ADD_SOURCE_INFO")

def add_area_id(dataset, add_uid = False):
  add_field(dataset, 'AreaID', 'TEXT')
  expression = "!FacilityOID!"
  if add_uid:
    uid = create_uuid()
    expression = f"str(!FacilityOID!) + '_' + '{uid}'"
      
  arcpy.management.CalculateField(dataset, "AreaID", 
                                expression, "PYTHON3")


def split_areas(points_fc):
  log.info(f'Splitter roder med mer enn {MAX_COUNT} bruksenheter...')
  la_analysis = create_location_allocation_analysis(LA_OPTIONS)

  add_area_id(points_fc)

  stats_table = summarize_by_area(points_fc, "AreaID")
  fields = ["AreaID", "COUNT_OBJECTID"]

  with arcpy.da.SearchCursor(stats_table, fields) as cursor:
    for row in cursor:
      if row[1] > MAX_COUNT:
        result_points = split_area(la_analysis, points_fc, row[0], row[1])
        add_area_id(result_points, True)
        update_points(points_fc, result_points, row[0])

  return points_fc