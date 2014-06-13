import threading
import gobject
import sys

import pygst
pygst.require('0.10')
import gst

from source_discovery import get_sources
from speech_parser import SpeechParser

def print_cb(name, uttid, text):
  print "(%s) %s: %s" % (uttid, name, text)

if __name__ == "__main__":
  gobject.threads_init()

  # Allow access by ID
  sources = get_sources()
  print "Discovered sources:"
  for src_id in sources:
    source = sources[src_id]
    print "(%d)\t%s\n\t%s\n" % (source['id'], source['name'], source['path'])

  print "\nWill now attempt to run speech-to-text on listed devices."
  raw_input("Press enter to begin: ")

  for (src_id, source) in sources.items():
    audiosrc = gst.element_factory_make("pulsesrc")
    audiosrc.set_property("device", source['id'])
    source['parser'] = SpeechParser(str(source['id']), audiosrc, print_cb, print_cb)

  # This loops the program until Ctrl+C is pressed
  g_loop = threading.Thread(target=gobject.MainLoop().run)
  g_loop.daemon = True
  g_loop.start()

  raw_input("Main loop is running. Press enter or Ctrl+C to exit.")

