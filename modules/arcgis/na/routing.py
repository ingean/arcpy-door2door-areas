import arcpy
from .network_dataset import create_network_dataset
from modules.arcgis.dataset import count_rows
from modules.object import set_attributes
from modules.log import Log
log = Log(arcgis=True)

defaults = {
  'travelMode': 'Gange',
  'findBestSequence': True
}

def create_route_analysis(options: dict, network: arcpy.nax.NetworkDataset = None) -> arcpy.nax.Route:
  """Creates and configures a route analysis 
     using ELVEG as default network"""

  nd = create_network_dataset(network)
  route = arcpy.nax.Route(nd)
  set_attributes(route, options, defaults)
  return route


def load_and_solve_route(route: arcpy.nax.Route, stops_fc: str):
  log.info(f'Loading {count_rows(stops_fc)} origins...')
  route.load(arcpy.nax.RouteInputDataType.Stops, stops_fc, None, False)

  log.info(f'Solving route with {count_rows(stops_fc)} stops...')
  return route.solve() 

def get_routes_cursor(result):
  if result.solveSucceeded:
    return result.searchCursor(arcpy.nax.RouteOutputDataType.Routes, ['Total_Minutes', 'Total_Kilometers'])
  else:
    log.warning(f'Not able to find a route for the provided stops')
    log.error(result.solverMessages(arcpy.nax.MessageSeverity.All))