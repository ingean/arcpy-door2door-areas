import os
import arcpy
from modules.log import Log
from modules.filepaths import Path
from modules.arcgis.dataset import delete_identical_features, get_path
from traveltime_pr_area import calculate_traveltime_pr_area

log = Log(arcgis=True)
arcpy.env.overwriteOutput = True

# For debugging
source_gdb = r'D:\Data\Kreftforeningen_roder\namsos.gdb'
#areas = os.path.join(source_gdb, 'roder_krk_bruksenheter')
areas = os.path.join(source_gdb, 'roder_krk_bruksenheter_split_single_merge')
#areas = os.path.join(source_gdb, 'roder_krk_bruksenheter_split_single')
points = os.path.join(source_gdb, 'Bruksenheter_i_krk_roder')
travelmode = 'Gange'

# Script inputs
#areas = arcpy.GetParameter(0) # Areas to enrich with statistics
#points = arcpy.GetParameter(1) # Points to visit within area
#travelmode = arcpy.GetParameter(2)

def enrich_areas() -> None:
  """Adds statistics to area, like point counts and total traveltime to visit
     each point in area"""

  p = Path(areas)
  result_areas = os.path.join(p.path, f'{p.filename}_statistics')

  log.info(f'Counting number of points within each area...')
  arcpy.analysis.SpatialJoin(areas, points, result_areas)

  log.info(f'Getting unique points...')
  unique_points = r'memory/unique_points'
  result = delete_identical_features(points, unique_points, None)

  log.info(f'Calculating traveltime for each area...')
  calculate_traveltime_pr_area(unique_points, result_areas, travelmode)

###############################################################################
enrich_areas()
