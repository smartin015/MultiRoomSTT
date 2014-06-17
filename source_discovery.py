from subprocess import Popen, PIPE
import re

def get_source_dump(): 
  """ Runs "pacmd list-sources" terminal command to get 
      a full dump of all sources known to pulse.
  """
  process = Popen(["pacmd", "list-sources"], stdout=PIPE, stderr=PIPE)
  (stdout, stderr) = process.communicate()
  if stderr:
    raise Exception(stderr)
  return stdout

def parse_source(text):
  """ Takes a segment of the terminal dump and parses out 
      source name, bus path, and id
  """
  id_m = re.search("(.+?)\n", text)
  if not id_m:
    raise Exception("Couldn't parse ID")
  src_id = int(id_m.group(1))

  name_m = re.search("name: <(.+?)>", text)
  if not name_m:
    raise Exception("Couldn't parse name")
  name = name_m.group(1)

  buspath_m = re.search("device.bus_path = \"(.+?)\"", text)
  if not buspath_m:
    raise Exception("Couldn't parse bus path")
  buspath = buspath_m.group(1)

  return {"id": src_id, "name": name, "path": buspath}

def get_sources():
  """ Repeatedly calls parse_source and rejects 
      non-input devices, before compiling them 
      into an id-indexed dictionary.
  """
  stdout = get_source_dump().split("index:")
  sources = dict()
  for text in stdout[1:]:
    source = parse_source(text)
    if not "input" in source['name']:
      continue
    sources[source['id']] = source
  return sources
