from flask import Flask, render_template, request, send_file, redirect
import os
import openai
import tempfile
from pydub import AudioSegment
import uuid
from flask_cors import CORS



app = Flask(__name__)
CORS(app)

# Set up the OpenAI API key
openai.api_key = ""

@app.route("/transkriber", methods=["POST"])
def transkriber():
    # Get the file from the POST request
    audio_file = request.files["myFile"]
    extension = request.form.get('extension')
    if extension == 'undefined':
        extension = '.txt'
    filename, file_extension = os.path.splitext(audio_file.filename)
    unique_id = str(uuid.uuid4())
    transcription_file_name = f"transcriptions/{unique_id}{extension}"
    # Set the duration (in seconds) of each smaller file
    split_duration = 180

    # Save the uploaded file to a temporary directory
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        audio_file.save(temp_file.name)
        # Load the MP3 file
        audio = AudioSegment.from_file(temp_file.name, format="mp3")

    # Get the duration of the MP3 file (in milliseconds)
    audio_length_ms = len(audio)

    # Calculate the number of smaller files that will be created
    num_splits = int(audio_length_ms / (split_duration * 1000)) + 1

    # Initialize an empty string to store the final transcript
    final_transcript = ""

    # Loop through the MP3 file and split it into smaller files
    for i in range(num_splits):
        # Set the start and end positions for each smaller file
        start_pos = i * split_duration * 1000
        end_pos = (i + 1) * split_duration * 1000
        if end_pos > audio_length_ms:
            end_pos = audio_length_ms

        # Extract the smaller file
        split_audio = audio[start_pos:end_pos]
        # Create a temporary file to store the split audio segment
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as split_temp_file:
            split_audio.export(split_temp_file.name, format="mp3")

            # Transcribe the split audio segment using the OpenAI API
            try:
                with open(split_temp_file.name, "rb") as audio_file:
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)
                    # Append the transcript to the final_transcript
                    final_transcript += transcript['text'] + "\n"
            except Exception as e:
                print(f"Failed to transcribe segment {i}: {e}")
                return "Failed to transcribe segment", 500

            # Remove the temporary file
#            os.remove(split_temp_file.name)

    # Save the final transcript to a file
    with open(transcription_file_name, "w", encoding="utf-8") as transcript_file:
        transcript_file.write(final_transcript)

    return transcription_file_name.rsplit('/', 1)[1]

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(app.root_path, 'transcriptions', filename)
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)