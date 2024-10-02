import platform
import subprocess
import warnings
import speech_recognition as sr
from queue import Queue
from whisper_model import Whisper
from datetime import datetime, timedelta
import numpy as np
import torch
import os
from time import sleep

LINUX = "linux"
WINDOWS = "windows"
MAC = "mac"

def get_operating_system():
    return platform.system().lower()

def check_for_dependencies(operating_system):
    # Check for system dependencies
    if operating_system == LINUX:
        # Check for pulseaudio
        process = subprocess.run(['which', 'pulseaudio'], capture_output=True, text=True)
        output = process.stdout.strip()
        if output:
            if "pulseaudio" not in output:
                warnings.warn("Pulseaudio not found. Please install pulseaudio with 'sudo apt install pulseaudio'")
                return False
        else:
            warnings.warn("Pulseaudio not found. Please install pulseaudio with 'sudo apt install pulseaudio'")
            return False
        
        # Check for pavucontrol
        process = subprocess.run(['which', 'pavucontrol'], capture_output=True, text=True)
        output = process.stdout.strip()
        if output:
            if "pavucontrol" not in output:
                warnings.warn("Pavucontrol not found. Please install pavucontrol with 'sudo apt install pavucontrol'")
                return False
        else:
            warnings.warn("Pavucontrol not found. Please install pavucontrol with 'sudo apt install pavucontrol'")
            return False
    elif operating_system == WINDOWS:
        # Check for dependencies
        pass
    elif operating_system == MAC:
        # Check for dependencies
        pass

    # Check for python dependencies
    # Check for pytorch
    try:
        import torch
    except ImportError:
        warnings.warn("PyTorch not found. Please install PyTorch. Visit PyTorch's website for installation instructions.")
        return False
    # Check if is cuda available
    if not torch.cuda.is_available():
        warnings.warn("CUDA not found in PyTorch installation. Please install PyTorch with CUDA support or install CUDA.")
        return False
    
    # Check for SpeechRecognition
    try:
        import speech_recognition as sr
    except ImportError:
        warnings.warn("SpeechRecognition not found. Please install SpeechRecognition with 'pip install SpeechRecognition' or 'conda install conda-forge::speechrecognition'")
        return False
    
    # Check for numpy
    try:
        import numpy as np
    except ImportError:
        warnings.warn("Numpy not found. Please install Numpy with 'pip install numpy' or 'conda install conda-forge::numpy'")
        return False
    
    # Check for pyaudio
    try:
        import pyaudio
    except ImportError:
        warnings.warn("PyAudio not found. Please install PyAudio with 'pip install pyaudio' or 'conda install conda-forge::pyaudio'")
        return False
    
    # Check for setuptools
    try:
        import setuptools
    except ImportError:
        warnings.warn("Setuptools not found. Please install Setuptools with 'pip install setuptools' or 'conda install conda-forge::setuptools'")
        return False
    
    # Check for whisper
    try:
        import whisper
    except ImportError:
        warnings.warn("Whisper not found. Please install Whisper with 'pip install git+https://github.com/openai/whisper.git'")
        return False
    
    return True

def list_sink_inputs():
    num_previous_lines = 50

    # Get sink inputs
    result = subprocess.run(["pactl", "list", "sink-inputs"], capture_output=True, text=True)
    
    # Parse sink inputs
    lines = result.stdout.splitlines()
    
    # List of sink inputs
    sink_inputs = []
    for i, line in enumerate(lines):
        if "application.name" in line:
            sink_input_app_name = line.split("=")[1].strip()
            if sink_input_app_name.startswith(' '):
                sink_input_app_name = sink_input_app_name[1:]
            for j in range(i, max(-1, i - num_previous_lines), -1):  # Find the sink input ID in the previous lines
                if "Sink Input" in lines[j]:
                    sink_input_id = lines[j].split("#")[1].strip()
                    sink_input = {"id": sink_input_id, "name": sink_input_app_name}
                    sink_inputs.append(sink_input)
    
    return sink_inputs

def list_microphones():
    microphones_list = [{"id": i, "name": name} for i, name in enumerate(sr.Microphone.list_microphone_names())]
    return microphones_list

def main():
    # Get operating system
    operating_system = get_operating_system()
    print(f"Operating System: {operating_system}")

    # Check for dependencies
    if not check_for_dependencies(operating_system):
        warnings.warn("Dependencies not met. Exiting...")
        return 1
    
    # Get devices to capture audio
    microphones = list_microphones()
    number_microphones = len(microphones)
    sink_inputs = list_sink_inputs()
    devices = microphones + sink_inputs
    number_devices = len(devices)
    print("\nInput devices:")
    for i, device in enumerate(devices):
        print(f"\t{i}. {device['name']}")
        if i == number_microphones - 1 and i < number_devices - 1:
            print("Applications:")
    print("Which device would you like to use?", end=" ")
    device_index = int(input())
    while device_index >= number_devices or device_index < 0:
        print("Invalid device index. Please enter a valid device index.")
        device_index = int(input())
    
    # If user select a microphone
    if device_index < number_microphones:
        device = microphones[device_index]
        print(f"Microphone selected: {device['name']}, id: {device['id']}")
        source = sr.Microphone(sample_rate=16000, device_index=device_index)
    else:
        device = sink_inputs[device_index - number_microphones]
        print(f"Application selected: {device['name']}, id: {device['id']}")
    
    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = 1000 # TODO args.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    # Load transcriber model
    print("Loading model...")
    transcriber = Whisper(model_size="small.en")

    record_timeout = 2 # TODO args.record_timeout
    phrase_timeout = 3 # TODO args.phrase_timeout

    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    # Cue the user that we're ready to go.
    print("Model loaded.\n")

    print_start = True

    while True:
        if print_start:
            print("Recording...")
            print_start = False
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now
                
                # Combine audio data from queue
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()
                
                # Convert in-ram buffer to something the model can use directly without needing a temp file.
                # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                # Read the transcription.
                result = transcriber.transcribe(audio_np, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                # If we detected a pause between recordings, add a new item to our transcription.
                # Otherwise edit the existing one.
                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                # Clear the console to reprint the updated transcription.
                # os.system('cls' if os.name=='nt' else 'clear')
                for line in transcription:
                    print(line)
                # Flush stdout.
                print('', end='', flush=True)
            else:
                # Infinite loops are bad for processors, must sleep.
                sleep(0.001)
        except KeyboardInterrupt:
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)


if __name__ == "__main__":
    main()