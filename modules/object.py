def set_attributes(obj: object, attributes: dict, defaults: dict = None):
  """Sets the object attributes to the values in the attributes dictionary or
     the defaults dictionary. Dictionary keys must have the same name as 
     object attributes."""
  
  if defaults is not None: 
    _set_attributes(obj, defaults)
  
  _set_attributes(obj, attributes)

  return obj


def _set_attributes(obj: object, attributes: dict):
  """Sets the object attributes to the values in the attributes dictionary. 
     Dictionary keys must have the same name as object attributes."""
  
  for key in attributes:
    setattr(obj, key, attributes[key])
  
  return obj


def get_value(options: dict, key: str, default):
  """Gets a value from a dictionary if key exists, else returns the default"""
  if options in key:
    return options[key]
  else:
    return default