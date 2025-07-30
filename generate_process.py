from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)
import os
from text_to_audio import text_to_speech_file
import time
import subprocess
from pathlib import Path as _Path  # optional: name clash avoid

# Use environment variables for portability
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "user_uploads")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "static/reels")
DONE_FILE = "done.txt"

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(DONE_FILE).touch(exist_ok=True)


def text_to_audio(folder):
    print("TTA -", folder)
    with open(os.path.join(UPLOAD_DIR, folder, "desc.txt")) as f:
        text = f.read()
    print(text, folder)
    text_to_speech_file(text, folder)  # Generates audio.mp3 inside folder


def create_reel(folder):
    input_txt = os.path.join(UPLOAD_DIR, folder, "input.txt")
    audio = os.path.join(UPLOAD_DIR, folder, "audio.mp3")
    output = os.path.join(OUTPUT_DIR, f"{folder}.mp4")

    command = f'''ffmpeg -f concat -safe 0 -i "{input_txt}" -i "{audio}" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p "{output}"'''
    subprocess.run(command, shell=True, check=True)
    print("CR -", folder)


if __name__ == "__main__":
    while True:
        print("Processing queue...")
        with open(DONE_FILE, "r") as f:
            done_folders = f.readlines()

        done_folders = [f.strip() for f in done_folders]
        folders = os.listdir(UPLOAD_DIR)

        for folder in folders:
            if folder not in done_folders:
                text_to_audio(folder)
                create_reel(folder)
                with open(DONE_FILE, "a") as f:
                    f.write(folder + "\n")

        time.sleep(4)
