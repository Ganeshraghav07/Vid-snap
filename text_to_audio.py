import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  
print("[DEBUG] KEY LOADED?", bool(os.getenv("ELEVENLABS_API_KEY")))


def text_to_speech_file(text: str, folder: str) -> str:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set. (.env/Render env me daalo)")
    client = ElevenLabs(api_key=api_key)

    upload_dir = os.getenv("UPLOAD_DIR", "user_uploads")
    out_dir = os.path.join(upload_dir, folder)
    os.makedirs(out_dir, exist_ok=True)

    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",
        output_format="mp3_22050_32",
        text=text or " ",
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=0.0, similarity_boost=1.0, style=0.0,
            use_speaker_boost=True, speed=0.9,
        ),
    )

    save_file_path = os.path.join(out_dir, "audio.mp3")
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"[VidSnap] Saved TTS audio: {save_file_path}")
    return save_file_path
