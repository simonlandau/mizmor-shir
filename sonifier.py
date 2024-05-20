from midiutil import MIDIFile
import os
import pickle
from io import BytesIO

# Constants
LETTERS = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]
EXT_MID_NUM = ["60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83"]
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11, 12],
    "minor": [0, 2, 3, 5, 7, 8, 10, 12],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11, 12],
    "chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "pentatonic": [0, 2, 4, 7, 9, 12],
    "blues": [0, 3, 5, 6, 7, 10, 12],
    "adonai_malakh": [0, 1, 2, 3, 5, 7, 9, 10, 12],
    "klezmer": [0, 1, 4, 5, 7, 8, 10, 12]
}
INSTRO_DICT = {
    "Harp": 46,
    "Piano": 1,
    "Trumpet": 57,
    "Flute": 74,
    "Violin": 41,
    "Guitar": 25,
}
VOLUME = 127  # 0-127, as per the MIDI standard
DURATION = 1  # In beats

# Scale by taking fifth root and normalize (between 0 and 1)
def normalize(arr: list[float], exp: float) -> list[float]:
    arr_min, arr_max = min(arr) ** exp, max(arr) ** exp
    for ind, val in enumerate(arr):
        arr[ind] = (val ** exp - arr_min) / (arr_max - arr_min)
    return arr

def quantize(arr: list[float], tones: int) -> list[int]:
        quant_arr = [0] * len(arr)
        for i in range(1, tones + 1):
            # Specify range for quantizing
            top = float(i) / tones
            bot = float(i - 1) / tones
            for ind, val in enumerate(arr):
                if val <= top and val >= bot:
                    # If entry is within range, assign to scale tone number (start counting from 0?)
                    quant_arr[ind] = i - 1
        return quant_arr

def generate_midi(root: str, scale: str, bpm: int, book: str, chapter: int, instrument: str) -> BytesIO:
    # Select scale
    scale = SCALES.get(scale, [])

    # Adjust scale based on root note
    root = root.lower()
    adj_start = LETTERS.index(root)
    adj_scale = [(note + adj_start) for note in scale]

    # Load pickle object
    directory = os.getcwd()
    with open(os.path.join(directory, "WORDS.pickle"), "rb") as f:
        WORDS = pickle.load(f)

    arr = WORDS[book][chapter - 1]
    arr = [val for val in arr if val != 0]  # Remove 0 values

    # Normalize and quantize data
    arr = normalize(arr, 0.2)
    arr = quantize(arr, len(adj_scale))

    # Map quantized values to adjusted scale
    comp = [adj_scale[val] for val in arr]
    comp_m = [int(EXT_MID_NUM[val]) for val in comp]

    # Select instrument
    program = INSTRO_DICT.get(instrument, 1)  # Default to Piano if not found

    # Write MIDI file
    realbpm = int(bpm)
    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created automatically)
    MyMIDI.addProgramChange(0, 0, 0, program)
    MyMIDI.addTempo(0, 0, realbpm)

    for i, pitch in enumerate(comp_m):
        MyMIDI.addNote(
            track=0,
            channel=0,
            pitch=pitch,
            time=i,
            duration=DURATION,
            volume=VOLUME,
        )

    midi_stream = BytesIO()
    MyMIDI.writeFile(midi_stream)
    midi_stream.seek(0)  # Rewind the buffer to the beginning
    return midi_stream
