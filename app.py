from flask import Flask, render_template, request, send_file
from sonifier import generate_midi
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/generate",methods = ['POST'])
def generate():
    # read in inputs from request
    root = request.form.get('root-note')
    scale = request.form.get('musical-scale')
    bpm = request.form.get('num-bpm')
    book = request.form.get('sel-torah')
    chapter = request.form.get('num-chap')
    instrument = request.form.get('sel-inst')

    # setting defaults for empty inputs
    # todo: validate inputs in javascript before sending to backend
    # maybe show error text in the input fields
    if(chapter == ""):
        chapter=2
    if(bpm == ""):
        bpm=120

    midi_content = generate_midi(root, scale, bpm, book, int(chapter), instrument)
    
    return send_file(
        midi_content,
        mimetype="audio/midi",
        as_attachment=True,
        download_name="output.mid"
    )

if __name__ == '__main__': app.run(debug=True)