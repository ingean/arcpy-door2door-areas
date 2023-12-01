import arcpy
arcpy.env.overwriteOutput = True

def features_to_aoi(input_dataset: str, output_dataset: str, buffer_distance: int) -> arcpy.Result:
  """Creates an AOI from clusters of features by buffering first with a large radius
     to merge adjacent features, and then performing a new negative buffer
    to reduce the outline"""

  negative_buffer_distance = -abs(buffer_distance * 0.9)

  arcpy.analysis.Buffer(
    input_dataset, r"memory\Buffers", buffer_distance, 
    "FULL", "ROUND", "ALL", None, "PLANAR")

  return arcpy.analysis.Buffer(
    r"memory\Buffers", output_dataset, negative_buffer_distance, 
    "FULL", "ROUND", "ALL", None, "PLANAR")