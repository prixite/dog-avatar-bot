import openai
from fastapi import APIRouter

router = APIRouter()


@router.post("transcribe_audio")
def transcribe_audio(payload_bytes_data):
    audio_file = payload_bytes_data
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    return transcript.text
