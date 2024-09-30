import whisper

class Whisper:
    def __init__(self, model_size="tiny"):
        self.model_size = model_size
        self.model = whisper.load_model(self.model_size)
    
    def transcribe(self, audio_np, fp16=False):
        return self.model.transcribe(audio_np, fp16=fp16)