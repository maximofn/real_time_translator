import platform
import subprocess
import warnings
import speech_recognition as sr

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
                print(f"\tj: {j}, lines[j]: {lines[j]}")
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


if __name__ == "__main__":
    main()