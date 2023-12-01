import arcpy
from .network_dataset import create_network_dataset
from modules.arcgis.dataset import count_rows
from modules.object import set_attributes
from modules.log import Log
log = Log(arcgis=True)

defaults = {
  'travelMode': 'Gange',
  'defaultImpedanceCutoff':15
}

def create_location_allocation_analysis(options: dict, network: arcpy.nax.NetworkDataset = None) -> arcpy.nax.LocationAllocation:
  """Creates and configures a location-allocation analysis 
     using ELVEG as default network"""

  nd = create_network_dataset(network)
  la = arcpy.nax.LocationAllocation(nd)
  set_attributes(la, options, defaults)
  return la

def load_and_solve_location_allocation(la: arcpy.nax.LocationAllocation, facilities: str, demand_points: str):
  log.info(f'Loading {count_rows(facilities)} facilities...')
  la.load(arcpy.nax.LocationAllocationInputDataType.Facilities, facilities, None, False)

  log.info(f'Loading {count_rows(demand_points)} demand points...')
  la.load(arcpy.nax.LocationAllocationInputDataType.DemandPoints, demand_points, None, False)

  log.info(f'Solving location-allocation for {la.facilityCount} facilities...')
  return la.solve()

def get_la_facilities(result, output_fc):
  log.info(f'Exporting facilities with status...')
  get_result_points(result, output_fc, arcpy.nax.LocationAllocationOutputDataType.Facilities)

def get_la_demand_points(result, output_fc):
  log.info(f'Exporting demand points with facility ids...')
  get_result_points(result, output_fc, arcpy.nax.LocationAllocationOutputDataType.DemandPoints)
  
def get_result_points(result, output_fc, result_type):
  if result.solveSucceeded:
    result.export(result_type, output_fc)
  else:
    log.error('Solving the location-allocation analysis failed! Message:')
    log.error(result.solverMessages(arcpy.nax.MessageSeverity.All)) 
