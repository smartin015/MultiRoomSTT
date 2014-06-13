import threading

import gobject
gobject.threads_init()

import pygst
pygst.require('0.10')
import gst

from source_discovery import get_sources
from command_parser import parser

if __name__ == "__main__":
  stdout = get_source_dump().split("index:")
  pipeline = gst.Pipeline()

  # Allow access by ID
  sources = get_sources()
  print "Discovered sources:"
  for source in sources:
    #source['gst'] = create_gst_src(source['id'])
    #pipeline.add(source['gst'])
    source['pad'] = None
    print "(%d) %s\n\t%s" % (source['id'], source['name'], source['path'])
  
  adder = gst.element_factory_make("adder", "audiomixer")
  sink = gst.element_factory_make("autoaudiosink", "audiosink")
  pipeline.add(adder, sink)
  adder.link(sink)

  bz = gst.element_factory_make("audiotestsrc")
  bz.set_property("freq", 440)
  pipeline.add(bz)
  sinkpad1 = adder.get_request_pad("sink%d")
  bz.get_pad("src").link(sinkpad1)

  pipeline.set_state(gst.STATE_PLAYING)

  # Start up gstreamer main loop
  #g_loop = threading.Thread(target=gobject.MainLoop().run)
  #g_loop.daemon = True
  #g_loop.start()

  bz2 = None
  sinkpad2 = None
  while True:
    cmd = raw_input("Select a source by ID: ")
    if not cmd:
      break
    src_id = int(cmd)
    #micsrc = sources[src_id]['gst'].get_pad("src")
    if sources[src_id]['pad']:
      print "Stopping source %d" % src_id
      bz2.get_pad("src").set_blocked(True)
      bz2.set_state(gst.STATE_NULL)
      bz2.get_pad("src").unlink(sinkpad1)
      adder.release_request_pad(sinkpad2)
      #micsrc.set_blocked(True)
      #micsrc.unlink(sources[src_id]['pad'])
      #adder.release_request_pad(sources
      sources[src_id]['pad'] = None
    else:
      print "Starting source %d" % src_id

      bz2 = gst.element_factory_make("audiotestsrc")
      bz2.set_property("freq", 560)
      pipeline.add(bz2)
      sinkpad2 = adder.get_request_pad("sink%d")
      bz2.get_pad("src").link(sinkpad2)
      bz2.set_state(gst.STATE_PLAYING)

      """
      sinkpad = adder.get_request_pad("sink%d")
      print sinkpad
      micsrc.link(sinkpad)
      #micsrc.set_blocked(False)
      sources[src_id]['gst'].set_state(gst.STATE_PLAYING) # TODO: Necessary?
      sources[src_id]['pad'] = sinkpad
      """
    sources[src_id]['pad'] = not sources[src_id]['pad']


