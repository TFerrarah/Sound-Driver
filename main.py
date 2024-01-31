import os
import time
from numpy import average
from AudioStreams import AudioStreams
from OBDHandler import OBDHandler


# Audio Stuff
cwd = os.getcwd();
separated_audio_dir = cwd+"/Audio/Separated/"
AUDIO_EXT = [".mp3", ".m4a", ".flac", ".wav"] # You can add more audio extensions here, as long as they are supported in ffplay

# Get audio files
original_song = cwd+"/Audio/Original.mp3"

# List of absolute paths for the component of the song
# This is done to ensure future-proofing to enable variations of other audio channels
# Only Bass, Drums, Vocals and "Other" channels will be used
audio_components = [separated_audio_dir+file for file in os.listdir(separated_audio_dir) if file.endswith(tuple(AUDIO_EXT))]

handler = OBDHandler()

loop = AudioStreams(audio_components) # ! THIS IS WHERE AUDIO STARTS PLAYING
zmq = "T:\Tommaso\Downloads\\ffmpeg-tools-2022-01-01-git-d6b2357edd\\ffmpeg-tools-2022-01-01-git-d6b2357edd\\bin\zmqsend.exe"

print(loop.get_streams_ports())

# Divide streams info
bass_port = loop.get_streams_ports()["Bass"]
drums_port = loop.get_streams_ports()["Drums"]
other_port = loop.get_streams_ports()["Other"]
vocals_port = loop.get_streams_ports()["Vocals"]

try:
    while True:
        time.sleep(0.05) # The less this value, the more accurate and responsive the audio change will be.

        frequencies = handler.get_frequencies()
        volumes = handler.get_volumes()

        # calculate lpf frequency

        bass_freq = average([frequencies["pedal"], frequencies["rpm"]], weights=[.5, 1])
        drums_freq = average([frequencies["pedal"], frequencies["rpm"], frequencies["speed"]], weights=[.2, .2, 1])
        other_freq = average([frequencies["pedal"], frequencies["rpm"], frequencies["speed"]], weights=[.2, .2, 1])
        vocals_freq = average([frequencies["speed"]], weights=[1])

        # Calculate volumes

        bass_vol = average([volumes["pedal"], volumes["rpm"]], weights=[.5, 1])
        other_vol = average([volumes["pedal"], volumes["rpm"], volumes["speed"]], weights=[.2, 1, .2])
        drums_vol = average([volumes["speed"]], weights=[1])
        vocals_vol = average([volumes["speed"]], weights=[1])

        # print([bass_freq, drums_freq, other_freq, vocals_freq])
        # print([bass_vol, drums_vol, other_vol, vocals_vol])
        # print(volumes)

        print(handler.get_percentages())

        # Set Volumes
        loop.change_vol(bass_vol, bass_port)
        loop.change_vol(drums_vol, drums_port)
        loop.change_vol(other_vol, other_port)
        loop.change_vol(vocals_vol, vocals_port)

        # Set LPF frequency
        loop.change_lpf(bass_freq, bass_port)
        loop.change_lpf(drums_freq, drums_port)
        loop.change_lpf(other_freq, other_port)
        loop.change_lpf(vocals_freq, vocals_port)
        

except KeyboardInterrupt:
    loop.stop_streams()
    print("\nGoodbye!")

loop.stop_streams()

