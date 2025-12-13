from transformers import WhisperProcessor, WhisperForConditionalGeneration
from peft import PeftModel
import torch
import librosa
import logging
import time

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load base model and LoRA adapter
base_model_name = "openai/whisper-large-v3"
adapter_path = "./model_full"

logger.info(f"Loading base model: {base_model_name}")
model = WhisperForConditionalGeneration.from_pretrained(base_model_name)

logger.info(f"Loading LoRA adapter from: {adapter_path}")
model = PeftModel.from_pretrained(model, adapter_path)

logger.info("Loading processor")
processor = WhisperProcessor.from_pretrained(base_model_name)

# Move to GPU if available, otherwise CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def transcribe(audio_path):
    logger.info(f"Transcribing audio file: {audio_path}")
    # Load and resample to 16kHz
    audio, sr = librosa.load(audio_path, sr=16000)
    
    logger.info(f"Resampled audio to 16kHz")
    
    # Process
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt")
    inputs = inputs.to(device)
    
    logger.info(f"Processed audio")
    
    # Generate with confidence scores
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_features,
            language="en",
            task="transcribe",
            return_dict_in_generate=True
        )
    
    logger.info(f"Generated with confidence scores")
    
    transcription = processor.batch_decode(outputs.sequences, skip_special_tokens=True)[0]
    
    return transcription

# Test it
start_time = time.time()
result = transcribe("../assets/call_1_calm.wav")
end_time = time.time()

print(f"\n{'='*60}")
print(f"Transcription: {result}")
print(f"{'='*60}")
print(f"Transcription time: {end_time - start_time:.2f} seconds")