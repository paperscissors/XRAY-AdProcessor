import time
import logging
from AdProcessor import AdProcessor


l = logging.getLogger("pydub.converter")
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())
start = time.time()

process = AdProcessor("beervana.mp3", "one.mp3", "two.mp3")

process.export("somefilename.mp3");

end = time.time()
print(end - start)
