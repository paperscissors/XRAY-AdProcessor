import uuid
import os
import sys
from pydub import AudioSegment


class AdProcessor:
    def __init__(self, episode, preroll, postroll=False, filename=False, amplitude=-20):
        self.amplitude = amplitude
        self.filename_uuid = str(uuid.uuid4())
        self.episode = self.load(episode)
        self.preroll = self.load(preroll)
        self.postroll = self.load(postroll) if postroll else False # postroll is optional

        self.export(filename)

    # detect leading silence on audio, so we can cut out awkward amounts of silence on beginning/end of files
    def detect_leading_silence(self, sound, silence_threshold=-50.0, chunk_size=10):
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

    # normalize sound amplitude so we don't get dips in audio levels
    def normalize(self, sound):
        change_in_dBFS = self.amplitude - sound.dBFS

        return sound.apply_gain(change_in_dBFS)

    # trim silence on beginning and end of audio; reverse audio to get end silence
    def trim_silence(self, audio):
        start_trim = self.detect_leading_silence(audio)
        end_trim = self.detect_leading_silence(audio.reverse())
        duration = len(audio)
        return audio[start_trim:duration-end_trim]

    # load audio file, run normalize and trim silence functions
    def load(self, filename):
        os.chdir(os.path.dirname(__file__))
        file_prefix, file_extension = os.path.splitext(filename)
        audio = AudioSegment.from_file(filename, file_extension.replace('.', ''))
        normalized_audio = self.normalize(audio)
        return self.trim_silence(audio)

    # actually concatenate spots and episode file. can override filename or use default with uuid
    def export(self, filename_override=False):
        files = [self.preroll, self.episode]

        if self.postroll:
            files.append(self.postroll)

        combined = files[0]

        for audio in files[1:]:
            combined = combined.append(audio, crossfade=50)

        filename = filename_override if filename_override else "episode-"+self.filename_uuid+".mp3"
        os.chdir(os.path.dirname(__file__))
        combined.export(os.getcwd()+'/results/'+filename, format="mp3", bitrate="320k")
        # i guess we can upload from here

        return True
