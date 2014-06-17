import threading
import gobject
import sys

import pygst
pygst.require('0.10')
import gst

from source_discovery import get_sources
from speech_parser import SpeechParser

# Put the absolute path to the *.dic and *.lm language model files
# here to supply a custom language model with higher translation accuracy.
# http://cmusphinx.sourceforge.net/wiki/tutoriallm
LM_PATH = None # *.lm goes here
DICT_PATH = None  # *.dic goes here

def partial_cb(name, uttid, text):
  """ This is called whenever Sphinx is in the middle of 
      transcribing an audio segment. Accuracy is much 
      lower here - it's trying to figure out what is 
      being said.
  """
  print "(%s) %s: %s" % (uttid, name, text)

def final_cb(name, uttid, text):
  """ This is called when sphinx finishes transcription.
      You should use this for speech commands, etc.
  """
  print "### (%s) %s: %s" % (uttid, name, text)

if __name__ == "__main__":
  gobject.threads_init()

  # Get a list of audio sources known to pulseaudio and display them
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
    source['parser'] = SpeechParser(
                          str(source['id']), 
                          audiosrc,
                          partial_cb, 
                          final_cb, 
                          LM_PATH, 
                          DICT_PATH
                       )

  # This loops the program until Ctrl+C is pressed
  g_loop = threading.Thread(target=gobject.MainLoop().run)
  g_loop.daemon = True
  g_loop.start()

  raw_input("Main loop is running. Press enter or Ctrl+C to exit.")

