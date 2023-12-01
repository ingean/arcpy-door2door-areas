import os
import arcpy
from modules.filepaths import Path
from modules.arcgis.dataset import export_dataset, count_rows, get_path
from modules.arcgis.conversion import features_to_aoi
from modules.arcgis.na.location_allocation import create_location_allocation_analysis, load_and_solve_location_allocation, get_la_demand_points
from modules.log import Log
from modules.utils import create_uuid
from traveltime_weight import calculate_traveltime_weight
from split_areas import split_areas

log = Log(arcgis=True)
arcpy.env.overwriteOutput = True

# Script inputs
municipality = arcpy.GetParameter(0)
selected_matrikkel_units = arcpy.GetParameter(1)
areas_to_create = arcpy.GetParameter(2)
units_area_factor_weight = arcpy.GetParameter(3)
max_units = arcpy.GetParameter(4) # Max units pr area to create
result_polys = arcpy.GetParameter(5)

# Analysis config
aoi_name_field = 'kommunenavn'
unit_type = 'Bolig'
unit_type_field = 'bruksenhetstype'
units_area_factor = 40 # 60 on previous runs
use_mean_distance_weight = True
use_travel_weight = False

aoi_buffer_size = 1000

""" options = {
  'decayFunctionType': arcpy.nax.DecayFunctionType.Power,
  'decayFunctionParameterValue': 2
} """

options = {
  'travelMode': 'Gange',
  'defaultImpedanceCutoff': 15,
  'problemType': arcpy.nax.LocationAllocationProblemType.MinimizeImpedance,
  'timeUnits': arcpy.nax.TimeUnits.Minutes
}

if max_units > 0:
  log.info(f'Setter maks antall bruksenheter pr rode til: {max_units}')
  options['problemType'] = arcpy.nax.LocationAllocationProblemType.MaximizeCapacitatedCoverage
  options['defaultCapacity'] = max_units

# Input dataset
input_gdb = r'D:\Data\Geodata Online\MATRIKKEL_BruksenhetPunkt.gdb'
matrikkel_units = os.path.join(input_gdb, 'MATRIKKEL_BruksenhetPunkt')

la_analysis = create_location_allocation_analysis(options)

def create_location_allocation_areas(aoi_name):
  global areas_to_create
  global use_mean_distance_weight
  
  if areas_to_create > 0: # Number of areas to find is set by user
    log.info(f'Finner et brukerdefinert antall områder ({areas_to_create})')
    use_mean_distance_weight = False
  
  # Create output dataset names
  #units_in_aoi = f'memory\AOI_Bruksenheter'
  result_ds = Path(str(result_polys))

  units_in_aoi = os.path.join(result_ds.path, f'AOI_Bruksenheter_{create_uuid()}')
  unique_units_in_aoi = r'memory\AOI_UnikeBruksenheter'
  
  aoi =  r'memory\AOI'
  result_points =  r'memory\AOI_RodePunkter'
  
  # Get demand points from Matrikkelen
  if aoi_name:
    query = f"{aoi_name_field} = '{aoi_name}' AND {unit_type_field} = '{unit_type}'"
    result = export_dataset(matrikkel_units, units_in_aoi, query)
  else:
    result = export_dataset(selected_matrikkel_units, units_in_aoi)
  
  units_count = count_rows(result[0])

  if areas_to_create == 0:
    areas_to_create = int(units_count / units_area_factor)

  log.info(f'{units_count} bruksenheter valgt ut som demand points i location-allocation')

  # Get facilites from Matrikkelen
  result2 = export_dataset(units_in_aoi, unique_units_in_aoi)
  arcpy.management.DeleteIdentical(unique_units_in_aoi, ['SHAPE'], '100 meters')
  unique_units_count = count_rows(result2[0])
 
  log.info(f'{unique_units_count} bruksenheter valgt ut som facilities i location-allocation')

  # Calculate travel weights
  if use_travel_weight:
    log.info(f'Kalkulerer nærhet til naboer index for {units_in_aoi}')
    calculate_traveltime_weight(units_in_aoi, 10)

  if use_mean_distance_weight:
    # Find unit point distribution for use in weighting
    stats = arcpy.stats.AverageNearestNeighbor(units_in_aoi, 'EUCLIDEAN_DISTANCE')
    log.info(f'Brukenhetenes spredningsindeks er: {stats[0]} (Mindre enn 1 betyr mer clustret enn spredt)')
    areas_to_create = int(units_count / (units_area_factor_weight - float(stats[0])*50))

  log.info(f'Antall roder for {municipality} er {areas_to_create}')

  # Create analysis AOI
  log.info(f'Avgrenser analyseområde for {municipality}')
  features_to_aoi(unique_units_in_aoi, aoi, aoi_buffer_size)

  # Create Location-Allocation analysis
  la_analysis.facilityCount = areas_to_create
  result = load_and_solve_location_allocation(la_analysis, unique_units_in_aoi, units_in_aoi)

  if result.solveSucceeded:
    get_la_demand_points(result, result_points)
    
    result_points = split_areas(result_points)

    log.info(f'Lager Thiessen polygoner fra resultatpunktene')
    arcpy.analysis.CreateThiessenPolygons(result_points, r'memory\ResultPolygons', "ALL")

    log.info(f'Slår sammen Thiessen polygoner med lik Facility ID')
    arcpy.management.Dissolve(r'memory\ResultPolygons', r'memory\ResultPolygonsDissolved', "AreaID", None, "SINGLE_PART", "DISSOLVE_LINES", '')
    
    log.info(f'Klipper polygonene til interesseområdet')
    arcpy.analysis.Clip(r'memory\ResultPolygonsDissolved', aoi, result_polys, None)

    log.info(f'Vellykket analyse av arealer :-)')

  else:
    log.error('Solving the location-allocation analysis failed:')
    log.error(result.solverMessages(arcpy.nax.MessageSeverity.All))

###############################################################################
create_location_allocation_areas(municipality)