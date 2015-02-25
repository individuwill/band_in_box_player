# Band in Box Player

This project was created for an engineering class at ASU (FSE 100). This program takes song pieces described in a specific format, and individual note recordings of an instrument, and outputs a track of the instrument playing its song.

The song clips are expected to be in stereo 16 bit wave format. The output will be a stereo 16 bit wav file of the complete song.

### Depenencies
+ pyaudio - for real time listening

### Usage
1. Describe your song in a text file.
2. Create recordings of the instrument's notes
3. Name the note recordings according to their representative notes
4. Modify the make_tracks.py file and point it to the correct files
5. Make any other neccessary adjustments in the make_track.py file such as BPM

An example song description has been included in the song_description folder. This song contains 4 different voices.

The make_tracks.py file is currently configured to process each voice of the song and output 4 separate tracks, one for each voice. It's default is not to play the song while creating it.
