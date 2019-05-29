from pydub import AudioSegment
import time
import logging
import uuid

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

amplitude = -20
filename = str(uuid.uuid4())
l = logging.getLogger("pydub.converter")
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())
start = time.time()

episode = AudioSegment.from_file("beervana.mp3", "mp3")

start_trim = detect_leading_silence(episode)
end_trim = detect_leading_silence(episode.reverse())
duration = len(episode)
trimmed_episode = episode[start_trim:duration-end_trim]

trimmed_episode = match_target_amplitude(trimmed_episode, amplitude)
adspot_1 = AudioSegment.from_file("one.mp3", "mp3")
adspot_2 = AudioSegment.from_file("two.mp3", "mp3")

adspot_1 = match_target_amplitude(adspot_1, amplitude)
adspot_2 = match_target_amplitude(adspot_2, amplitude)

files = [adspot_1, trimmed_episode, adspot_2]

combined = files[0]

for audio in files[1:]:
    combined = combined.append(audio, crossfade=50)

combined.export("episode-"+filename+".mp3", format="mp3", bitrate="256k")

end = time.time()
print(end - start)
