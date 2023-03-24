from mido import Message, MidiFile, MidiTrack
import mido
from flask import Flask, render_template, request, send_file


app = Flask(__name__)


# Функция для преобразования дроби в число с плавающей точкой
def fraction_to_float(fraction_str):
    numerator, denominator = fraction_str.split('/')
    return float(numerator) / float(denominator)


# Функция для преобразования текстовой нотации в список кортежей (нота, длительность)
def parse_notes(notes_string):
    notes = notes_string.split()
    parsed_notes = []
    for note in notes:
        if '(' in note:
            pitch, duration = note.split('(')
            if '/' in duration:
                duration = fraction_to_float(duration[:-1])
            else:
                duration = float(duration[:-1])
        else:
            pitch = note
            duration = 0.25
        parsed_notes.append((pitch, duration))
    return parsed_notes


# Функция для преобразования ноты в MIDI-номер
def note_to_midi_number(note):
    note_names = ['C', 'C#', 'D', 'D#', 'E',
                  'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = int(note[-1])
    pitch_class = note[:-1]
    print(f"octave: {octave}, pitch_class: {pitch_class}")
    midi_number = (octave * 12) + note_names.index(pitch_class)
    return midi_number


def parse_notes(notes_string):
    notes = notes_string.split()
    parsed_notes = []
    for note in notes:
        if '(' in note:
            pitch, duration = note.split('(')
            duration = fraction_to_float(duration[:-1])
            print(f"pitch: {pitch}, duration: {duration}")
        else:
            pitch = note
            duration = 0.25
        parsed_notes.append((pitch, duration))
    return parsed_notes


# Создание MIDI-файла из списка нот и настроек
def create_midi_file(parsed_notes, output_file, tempo, velocity):
    midi_file = MidiFile()
    track = MidiTrack()
    midi_file.tracks.append(track)

    # Добавьте событие установки темпа
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))

    for note, duration in parsed_notes:
        midi_number = note_to_midi_number(note)
        note_on = Message('note_on', note=midi_number,
                          velocity=int(velocity), time=0)
        note_off = Message('note_off', note=midi_number,
                           velocity=int(velocity), time=int(duration * 480))
        track.append(note_on)
        track.append(note_off)

    midi_file.save(output_file)


# Преобразование MIDI-файла в текстовую нотацию
def midi_to_text(input_filepath):
    def note_name(midi_number):
        note_names = ['C', 'C#', 'D', 'D#', 'E',
                      'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = midi_number // 12
        pitch_class = midi_number % 12
        return note_names[pitch_class] + str(octave)

    try:
        midi_file = MidiFile(input_filepath)
        note_events = []
        current_time = 0
        for track in midi_file.tracks:
            for msg in track:
                current_time += msg.time

                if msg.type == 'note_on' and msg.velocity > 0:
                    note_events.append((current_time, 'note_on', msg.note))

                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    note_events.append((current_time, 'note_off', msg.note))

        notes = []
        note_on_dict = {}

        for event in note_events:
            if event[1] == 'note_on':
                note_on_dict[event[2]] = event[0]

            elif event[1] == 'note_off':
                start_time = note_on_dict[event[2]]
                end_time = event[0]
                duration = (end_time - start_time) / midi_file.ticks_per_beat
                notes.append((note_name(event[2]), duration))

        text_notes = ''

        for note, duration in notes:
            if duration != 0.25:
                text_notes += f"{note}({duration:.3f}) "
            else:
                text_notes += f"{note} "

        return text_notes.strip()
    except Exception as e:
        print(e)
        return "Error converting MIDI file"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        notes_string = request.form['notes_string']
        tempo = int(request.form['tempo'])
        velocity = int(request.form['velocity'])
        parsed_notes = parse_notes(notes_string)
        output_filename = 'output.mid'
        create_midi_file(parsed_notes, output_filename, tempo, velocity)

        return send_file(output_filename, as_attachment=True)
    return render_template('index.html')


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'POST':
        input_file = request.files['input_file']
        output_filename = 'output.txt'
        input_file.save(input_file.filename)
        output_text = midi_to_text(input_file.filename)
        with open(output_filename, 'w') as f:
            f.write(output_text)
        return send_file(output_filename, as_attachment=True)
    return render_template('convert.html')


if __name__ == '__main__':
    app.run(debug=False, port=8000)
