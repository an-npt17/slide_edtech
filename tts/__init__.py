import io
from gtts import gTTS
from flask import (
    request, 
)


def read_content():
    text = request.form['text']
    lang = request.form['lang']
    tts = gTTS(text=text, lang=lang)

    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    data = buffer.read()
    return data