import time
import logging
from AdProcessor import AdProcessor

# example of AdProcessor use with debugging
l = logging.getLogger("pydub.converter")
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())
start = time.time()

process = AdProcessor("beervana.mp3", "one.mp3", "two.mp3") # postroll is totally optional

process.export("somefilename.mp3"); # example with filename override

end = time.time() # print out time of execution for debugging purposes
print(end - start)
