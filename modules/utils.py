import uuid
from .log import Log

log = Log(arcgis=True)

def create_uuid() -> str:
  """Creates a unique id/guid (uuid4) as a string"""
  
  return str(uuid.uuid4()).replace('-', '_')