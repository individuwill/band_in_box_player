#!/usr/bin/env python
# wav files - http://www.topherlee.com/software/pcm-tut-wavformat.html
import pyaudio
import wave
import sys
import struct
import os

AUDIBLE = False
OUTPUT_NAME = 'pan_flute.wav'
#INSTRUMENT_DIRECTORY = 'flute'
INSTRUMENT_DIRECTORY = '../Audio/pan_flute/for_track'
#SONG_FILE = 'ode_high.txt'
SONG_FILE = 'ode_mid_high.txt'
FPS = 44100
SAMPLE_WIDTH = 2
CHANNELS = 2
NP = 0.10

def fade(data, numframes):
    fade_frames = int(0.05 * FPS * CHANNELS)
    print numframes, fade_frames
    new_data = list(struct.unpack('%sh' % (numframes*CHANNELS), data))
    # smooth out first .1 of a second in even steps from 0 to
    # samples maximum amplitude
    max_amplitude = 0
    for n in range(0, fade_frames):
        max_amplitude = max(max_amplitude, abs(new_data[n]))
    print 'max amplitude: %s' % (max_amplitude)

    slope = max_amplitude / (1.0 * fade_frames)
    print 'slope: ' + str(slope)
    start_faded_data = []
    for x in range(0, fade_frames):
        y = slope * x
        percent_scale = y / max_amplitude
        start_faded_data.append(new_data[x]*percent_scale)

    end_faded_data = []
    for x in range(fade_frames, 0, -1):
        y = slope * x
        percent_scale = y / max_amplitude
        end_faded_data.append(new_data[len(new_data)-x]*percent_scale)

    new_new_data = start_faded_data + new_data[len(end_faded_data)-1:-len(end_faded_data)] + end_faded_data
    print '%i' % (len(new_new_data))
    #print new_new_data
    #new_data = map(lambda d: d/10, new_data)
    return struct.pack('%ih' % (len(new_new_data)), *new_new_data)
    #return data

def get_tones(directory):

    instrument_file_names = filter(lambda f: len(f) < 8,
            os.listdir(directory))
    instrument_files = [os.path.join(directory,f) for f in
        instrument_file_names]
    instrument_notes = [f.split('.')[0].replace('s', '#') for f in instrument_file_names]

    tones = {}
    for n, f in zip(instrument_notes, instrument_files):
        tones[n] = wave.open(f, 'rb')
    return tones

def get_song(song_file):
    song_text = filter(lambda l: l.strip() != '',
            open(song_file, 'rb').read().split('\n'))
    notes = []
    for line in song_text:
        line_notes = filter(lambda n: n.strip() != '',
                line.split(','))
        for note in line_notes:
            note_data = tuple(note.strip().split(' '))
            notes.append(note_data)
            #print note_data
        #print line_notes
    #print song_text
    return notes

BPM = 120
bps = BPM/60.0
beat_length = 1.0/bps
NOTE_LENGTHS = {
    'Q' : beat_length,
    'H' : 2*beat_length, # half note
    'W' : 4*beat_length, # whole note
    'E' : beat_length/2.0, # eigth note
    'S' : beat_length/4.0, # sixteenth
    'DQ' : beat_length + beat_length/2.0}
silence = (struct.pack('h', 0) * int(FPS * NP)) * SAMPLE_WIDTH

p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(SAMPLE_WIDTH),
        channels=CHANNELS,
        rate=FPS,
        output=True)

# process external note files and song description
tones = get_tones(INSTRUMENT_DIRECTORY)
song = get_song(SONG_FILE)

# setup wave output file
of = wave.open(OUTPUT_NAME, 'wb')
of.setnchannels(CHANNELS)
of.setsampwidth(SAMPLE_WIDTH)
of.setframerate(FPS)

# play and or write song
for n in song:
    note = n[0]
    length = NOTE_LENGTHS[n[1]]
    slur = False
    if len(n) == 3 and n[2] == 'slur':
        slur = True

    wf = tones[note]
    wf.rewind()
    if slur:
        numframes = int(FPS * length)
    else:
        numframes = int(FPS * (length - NP))

    data = wf.readframes(numframes)
    data = fade(data, numframes)

    if AUDIBLE:
        stream.write(data)
        if not slur:
            stream.write(silence)

    of.writeframes(data)
    if not slur:
        of.writeframes(silence)
    
# cleanup audible output
stream.stop_stream()
stream.close()
p.terminate()