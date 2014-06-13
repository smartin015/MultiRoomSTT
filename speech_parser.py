#!/usr/bin/env python
import pygst
pygst.require('0.10')
import gst

class SpeechParser():

  def __init__(self, name, audiosrc, partial_cb, full_cb):
    # Partial and full callbacks must take arguments 
    # (name, uttid, text)
    self.name = name
    self.partial_cb = partial_cb
    self.full_cb = full_cb
    self.pipe = gst.Pipeline()
    
    conv = gst.element_factory_make("audioconvert", "audioconv")
    res = gst.element_factory_make("audioresample", "audioresamp")
    
    vader = gst.element_factory_make("vader", "vad")
    vader.set_property("auto-threshold", True)
    
    asr = gst.element_factory_make("pocketsphinx", "asr")
    asr.connect('partial_result', self.asr_partial_result)
    asr.connect('result', self.asr_result)
    asr.set_property('configured', True)
    
    sink = gst.element_factory_make("fakesink", "fs")
    
    self.pipe.add(audiosrc, conv, res, vader, asr, sink)
    gst.element_link_many(audiosrc, conv, res, vader, asr, sink)
    self.pipe.set_state(gst.STATE_PLAYING)
   
  def pause(self):
    self.pipe.set_state(gst.STATE_PAUSED)

  def play(self):
    self.pipe.set_state(gst.STATE_PLAYING)

  def asr_partial_result(self, asr, text, uttid):
    """ This function is called when pocketsphinx gets a partial
        transcription of spoken audio. 
    """
    self.partial_cb(self.name, uttid, text)
    
  def asr_result(self, asr, text, uttid):
    """ This function is called when pocketsphinx gets a 
        full result (spoken command with a pause)
    """
    self.full_cb(self.name, uttid, text)

if __name__ == "__main__":
  import threading
  import gobject 
  gobject.threads_init()

  def print_cb(name, uttid, text):
    print "(%s) %s: %s" % (uttid, name, text)

  src = gst.element_factory_make("autoaudiosrc")
  parser = SpeechParser("parser", src, print_cb, print_cb)

  # This loops the program until Ctrl+C is pressed
  g_loop = threading.Thread(target=gobject.MainLoop().run)
  g_loop.daemon = False
  g_loop.start()
