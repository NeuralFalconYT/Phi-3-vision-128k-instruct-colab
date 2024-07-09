from pydub import AudioSegment
import os 
import cv2
import os
import uuid
from PIL import Image
import cv2
import simpleaudio as sa
import threading
from gradio_client import Client,file

app_url="https://348c7c8264c36c9e39.gradio.live/" 
#make sure app_url ends with a slash
try:
    client = Client(app_url)
except:
    print("Error: Could not connect to the server. Please make sure the URL is correct and the server is running.")

def mp3_to_wav(mp3_file, wav_file):
    sound = AudioSegment.from_mp3(mp3_file)
    sound.export(wav_file, format="wav")


if not os.path.exists("./compressed_image"):
    os.makedirs("./compressed_image")
if not os.path.exists("./audio"):
    os.makedirs("./audio")
# Generate a random image file name
def generate_image_name():
    # return f'./compressed_image/{str(uuid.uuid4())[:8]}.jpg'
    return f'./compressed_image/temp.jpg'

def compress_image(frame, quality=50):
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    convert_pil = Image.fromarray(frame_rgb)
    output_image_path = generate_image_name()
    convert_pil.save(output_image_path, optimize=True, quality=quality)
    return output_image_path


def play_audio(filename):
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def describe_image(prompt, image_file):
	if len(prompt) == 0:
		prompt = "Describe the image in single sentence"

	result = client.predict(
			prompt, 
			file(image_file),	
			api_name="/predict"
			)
	# print(result)
	mp3_file = result
	base_path = os.path.basename(mp3_file).split(".")[0]
	wav_file = f"./audio/{base_path}.wav"
	mp3_to_wav(mp3_file, wav_file)
	play_audio(wav_file)    
from whisper_mic import WhisperMic

mic = WhisperMic(model="tiny.en")
def speech_recognition():
    while True:  
        try:
            text = mic.listen()
            print("You said:", text)
            
            pronunciations = ["alisha", "alisa", "alyssa"]  # Add any variations you want to consider

            matching_variation = next((variation for variation in pronunciations if variation in text.lower()), None)

            if matching_variation:
                print(f"Matched variation: {matching_variation}")
                print("Triggering the API...")
                play_audio("okay.wav")
                prompt = text.lower().split(matching_variation)[-1].strip()
                prompt = prompt.strip().replace(",", " ").strip()
                print("Prompt:", prompt)
                upload_image = compress_image(frame)
                print(upload_image)
                describe_image(prompt, upload_image)
    
        except Exception as e:
            print(e)

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    speech_thread = threading.Thread(target=speech_recognition)
    speech_thread.start()

    while True:
        ret, frame = cap.read()
        cv2.imshow('Webcam', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
 
