import arcpy
arcpy.env.overwriteOutput = True

def create_network_dataset(path:str = None, name:str = None) -> arcpy.nax.NetworkDataset:
  """Create a network dataset for analysis that defaults to ELVEG."""

  name = name if name is not None else f"Vegnettverk (ELVEG)"
  path = path if path is not None else r'D:\Data\Geodata Online\ELVEG_Nettverk.gdb\ELVEG_Nettverk\ELVEG_Nettverk_ND'
  return arcpy.nax.MakeNetworkDatasetLayer(path, name)

 
