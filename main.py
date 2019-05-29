import time
import logging
from AudioProcessor import AudioProcessor


l = logging.getLogger("pydub.converter")
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())
start = time.time()

process = AudioProcessor("beervana.mp3", "one.mp3", "two.mp3")

process.trim_silence().export("somefilename.mp3");

end = time.time()
print(end - start)
