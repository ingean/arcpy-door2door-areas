import arcpy
from modules.arcgis.dataset import count_rows
from .network_dataset import create_network_dataset
from modules.object import set_attributes
from modules.log import Log
log = Log(arcgis=True)

defaults = {
  'travelMode': 'Gange',
  'defaultImpedanceCutoff':15
}

def create_origin_destination_analysis(options: dict, network: arcpy.nax.NetworkDataset = None) -> arcpy.nax.OriginDestinationCostMatrix:
  """Creates and configures a origin destination matrix analysis 
     using ELVEG as default network"""
  
  log.info('Creating and configuring OD Matrix analysis...')
  nd = create_network_dataset(network)
  od_matrix = arcpy.nax.OriginDestinationCostMatrix(nd)
  set_attributes(od_matrix, options, defaults)
  return od_matrix

def load_and_solve_od_matrix(od_matrix, origins_fc, destinations_fc):
  log.info(f'Loading {count_rows(origins_fc)} origins...')
  od_matrix.load(arcpy.nax.OriginDestinationCostMatrixInputDataType.Origins, origins_fc, None, False)

  log.info(f'Loading {count_rows(destinations_fc)} as destinations...')
  od_matrix.load(arcpy.nax.OriginDestinationCostMatrixInputDataType.Destinations, destinations_fc, None, False)
  
  log.info(f'Solving OD Matrix finding {od_matrix.defaultDestinationCount} destinations for each origin...')
  return od_matrix.solve()

def get_od_lines(result, output_fc: str) -> None:
  if result.solveSucceeded:
    log.info(f'Exporting resulting OD matrix lines...')
    result.export(arcpy.nax.OriginDestinationCostMatrixOutputDataType.Lines, output_fc)
  else:
    log.error('Solving the od matrix failed! Message: ')
    log.error(result.solverMessages(arcpy.nax.MessageSeverity.All))