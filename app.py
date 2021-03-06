from flask import Flask, render_template, request, session
#from csv import DictReader
from midiutil import MIDIFile
import os
import random
import pickle
import string
import boto3
from botocore.client import Config

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str

def makeMusic(root_note, musical_scale, num_bpm, sel_torah, sel_chap, sel_inst):

    print("Entering the make music function")

    i = 0
    j = 0

    degrees = [0,1,2,3,4,5,6,7,8,9,10,11]
    letters = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]
    mid_num = ["60","61","62","63","64","65","66","67","68","69","70","71"]


    ext_degrees = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    ext_letters = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b","c'", "c#'", "d'", "d#'", "e'", "f'", "f#'", "g'", "g#'", "a'", "a#'", "b'"]
    ext_mid_num = ["60","61","62","63","64","65","66","67","68","69","70","71","72","73","74","75","76","77","78","79","80","81","82","83"]

    major = [0,2,4,5,7,9,11,12]
    minor = [0,2,3,5,7,8,10,12]
    harmonic_minor = [0,2,3,5,7,8,11,12]
    chromatic = [0,1,2,3,4,5,6,7,8,9,10,11,12]
    pentatonic = [0,2,4,7,9,12]
    blues = [0,3,5,6,7,10,12]
    adonai_malakh = [0,1,2,3,5,7,9,10,12]
    klezmer = [0,1,4,5,7,8,10,12]

    scale = []

    if musical_scale == "major":
        scale.extend(major)
    elif musical_scale == "harmonic_minor":
        scale.extend(harmonic_minor)
    elif musical_scale == "chromatic":
        scale.extend(chromatic)
    elif musical_scale == "minor":
        scale.extend(minor)
    elif musical_scale == "pentatonic":
        scale.extend(pentatonic)
    elif musical_scale == "blues":
        scale.extend(blues)
    elif musical_scale == "adonai_malakh":
        scale.extend(adonai_malakh)
    elif musical_scale == "klezmer":
        scale.extend(klezmer)

    root_note = root_note.lower()

    adj_start = letters.index(root_note)
    adj_scale = []

    for i in range(len(scale)):
        adj_scale.append((scale[i] + adj_start)) #Maybe add Mod 13 ... will keep in same octave but will jump around

    print(adj_scale)

    comp = []

    directory = os.getcwd()

    with open(directory + "/MATRIX.pickle", "rb") as f:
        MATRIX = pickle.load(f)


    # Load pickle object
    with open(directory + "/WORDS.pickle", "rb") as f:
        WORDS = pickle.load(f)

    # tones is number of notes in scale
    tones = len(adj_scale)
    sel_torah = str(sel_torah)
    sel_chap = int(sel_chap)
    # chap is the desired chapter number, book is desired book
    book, chap = sel_torah, sel_chap
    # arr is the desired list of data (subtract 1 from chapter bc count from 0, not 1)
    arr = WORDS[book][chap - 1]

    # Remove 0 values
    while 0 in arr:
        arr.remove(0)

    # Scale by taking fifth root and normalize (between 0 and 1)
    def normalize(arr, exp):
        arr_min, arr_max = min(arr) ** exp, max(arr) ** exp
        for ind, val in enumerate(arr):
            arr[ind] = (val ** exp - arr_min) / (arr_max - arr_min)
        return arr

    arr = normalize(arr, 0.2)

    # Quantize values by mapping certain ranges to certain scale tones
    def quantize(arr, tones):
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

    arr = quantize(arr, tones)

    print(arr)

    for i in range(len(arr)):
        comp.append(adj_scale[arr[i]])


    comp_m = []


    for i in range(len(comp)):
        comp_m.append(ext_mid_num[comp[i]])


    for i in range(len(comp_m)):
        comp_m[i] = int(comp_m[i])

    ################ Choose instrument #######################################

    instro_dict = {
    "Harp" : 46,
    "Piano" : 1,
    "Trumpet" : 57,
    "Flute" : 74,
    "Violin" : 41,
    "Guitar" : 25
    }

    ###################### Write Midi File ##################################

    realbpm = int(num_bpm)

    track    = 0
    track1   = 1
    track2   = 2
    track3   = 3
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = realbpm # num_bpm  # In BPM
    volume   = 127  # 0-127, as per the MIDI standard
    program = instro_dict[sel_inst] #instrument -- look up on https://www.midi.org/specifications-old/item/gm-level-1-sound-set

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
    MyMIDI.addProgramChange(track, channel, time, program)                      # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(comp_m):
        MyMIDI.addNote(track, channel, pitch, time + i, duration, volume, program)

    filename = get_random_string(8) + '.mid'

    with open(filename, 'wb') as output_file:
        MyMIDI.writeFile(output_file)

    ACCESS_KEY_ID = 'REDACTED'
    ACCESS_SECRET_KEY = 'REDACTED'
    BUCKET_NAME = 'REDACTED'

    data = open(filename, 'rb')

    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )

    s3.Bucket(BUCKET_NAME).put_object(Key=filename, Body=data)

    return filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/generate",methods = ['GET'])
def generate():
    
    # read in inputs from request
    rootnote = request.args.get('root-note')
    musicalscale = request.args.get('musical-scale')
    numbpm = request.args.get('num-bpm')
    seltorah = request.args.get('sel-torah')
    numchap = request.args.get('num-chap')
    selinst = request.args.get('sel-inst')

    if(numchap == ""):
        numchap=2

    if(numbpm == ""):
        numbpm=120

    session['filename'] = makeMusic(rootnote, musicalscale, numbpm, seltorah, numchap, selinst)
    session['rootnote'] = rootnote
    session['musicalscale'] = musicalscale
    session['numbpm'] = numbpm
    session['seltorah'] = seltorah
    session['numchap'] = numchap
    session['instrument'] = selinst
    session['sefariaurl'] = seltorah + "." + str(numchap)
    session['text'] = seltorah + " " + str(numchap) 

    return render_template("player.html")

if __name__ == '__main__': app.run(debug=True)