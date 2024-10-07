import platform
import warnings
import subprocess
# import speech_recognition as sr
# from queue import Queue
from whisper_model import Whisper
from translator import Translator
# from llama_3_1_1B import Llama_3_1_1B
# from datetime import datetime, timedelta
# import numpy as np
# import torch
# import os
# from time import sleep
# import pyaudio
from sink_device import Sink_device
from source_device import Source_device

LINUX = "linux"
WINDOWS = "windows"
MAC = "mac"

def get_operating_system():
    return platform.system().lower()

def check_for_dependencies(operating_system):
    # Check for system dependencies
    if operating_system == LINUX:
        # Check for pulseaudio
        # process = subprocess.run(['which', 'pulseaudio'], capture_output=True, text=True)
        # output = process.stdout.strip()
        # if output:
        #     if "pulseaudio" not in output:
        #         warnings.warn("Pulseaudio not found. Please install pulseaudio with 'sudo apt install pulseaudio'")
        #         return False
        # else:
        #     warnings.warn("Pulseaudio not found. Please install pulseaudio with 'sudo apt install pulseaudio'")
        #     return False
        
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
        
        # TODO libasound2-plugins libasound2-dev libpulse-dev pulseaudio python3-pyaudio pipewire-alsa
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
        warnings.warn("PyTorch not found. Please install PyTorch. Visit PyTorch website for installation instructions.")
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
    # TODO ollama
    
    return True

def list_sink_devices(debug=False):
    # Get output audio devices
    result = subprocess.run(["pactl", "list", "sinks"], capture_output=True, text=True)
    if result:
        output = result.stdout
        sink_devices_list = []
        sink_device = None
        for number_line, line in enumerate(output.split("\n")):
            if "Sink #" in line or "Destino #" in line:
                if sink_device: # If not the first device append the previous device to the list
                    sink_devices_list.append(sink_device)
                sink_device = {"id": line.split("#")[1]}
                if debug: print(f"\tOutput device: {sink_device['id']}")
                properties = 0
                ports = 0
                formats = 0
            elif "Properties:" in line:
                properties = 1
                ports = 0
                formats = 0
                sink_device["properties"] = {}
            elif "Ports:" in line:
                properties = 0
                ports = 1
                formats = 0
                sink_device["ports"] = {}
            elif "Formats:" in line:
                properties = 0
                ports = 0
                formats = 1
                sink_device["formats"] = {}
            else:
                key = line.split(":")[0].strip()
                if "balance" in key:
                    key = "balance"
                    value = line.split("balance")[1]
                else:
                    value = line.split(":")[1:]

                # if value is a list, join it
                if type(value) == list:
                    value = "".join(value).strip()
                else:
                    value = value.strip()

                if properties:
                    sink_device["properties"][key] = value
                elif ports:
                    sink_device["ports"][key] = value
                elif formats:
                    if key != "":
                        sink_device["formats"][key] = value
                else:
                    sink_device[key] = value
            
            if number_line == len(output.split("\n")) - 1:
                sink_devices_list.append(sink_device)

    return sink_devices_list

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
    
    # Get sink devices to capture audio
    # sink_device = Sink_device()
    # source_device = Source_device()

    # Select audio device
    # select_sink = False
    # select_source = False
    # devices = sink_device.sink_devices_list + source_device.source_devices_list
    # print("\nInput devices:")
    # for i, device in enumerate(devices):
    #     if "Description" in device.keys():
    #         print(f"\t{i:02}. {device['Description']}")
    #     else:
    #         print(f"\t{i:02}. {device['Descripción']}")
    # print("Which device would you like to use?", end=" ")
    # device_index = int(input())
    # while device_index < 0 or device_index >= len(devices):
    #     print("Invalid device index. Please enter a valid device index.")
    #     device_index = int(input())
    # if device_index < len(sink_device.sink_devices_list):
    #     result = sink_device.asign_sink_device(device_index)
    #     if result:
    #         print(f"Sink device selected: {sink_device.sink_device['Description']}, id: {sink_device.sink_device['id']}")
    #         select_sink = True
    # else:
    #     device_index -= len(sink_device.sink_devices_list)
    #     result = source_device.asign_source_device(device_index)
    #     if result:
    #         print(f"Source device selected: {source_device.source_device['Description']}, id: {source_device.source_device['id']}")
    #         select_source = True
    
    # Load transcriber and translate model
    print("Loading model...")
    # transcriber = Whisper(model_size="small.en")
    translator = Translator()
    print("Model loaded.")
    translate_text = translator.translate("Hello, how are you?")
    print(f"Translated text: {translate_text}")
    return 0

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
                    translate_text = translator.translate(line)
                    print(f"{line}\t\t{translate_text}")
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