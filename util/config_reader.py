from configparser import ConfigParser

class ConfigReader:

  def __init__(self, config_filename):
    self.config_filename = config_filename
    self.config_parser = ConfigParser()
    with open(self.config_filename) as stream:
      self.config_parser.read_string("[root]\n" + stream.read())

  def get(self, parameter, type):
    value = self.config_parser.get("root", parameter)
    value = value.split("#")[0].strip()
    if type == "int":
      return int(value)
    elif type == "float":
      return float(value)
    elif type == "bool":
      return value == "true"
    else:
      return str(value)