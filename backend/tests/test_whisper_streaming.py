from transformers import WhisperProcessor, WhisperForConditionalGeneration
from peft import PeftModel
import torch
import librosa
import logging
import time
import numpy as np

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

def transcribe_streaming(audio_path, chunk_length=10, overlap=2):
    """
    Transcribe audio in chunks with overlap for streaming effect.

    Args:
        audio_path: Path to audio file
        chunk_length: Length of each chunk in seconds (default: 10s)
        overlap: Overlap between chunks in seconds (default: 2s)

    Yields:
        Tuples of (chunk_text, chunk_start_time, chunk_end_time, processing_time)
    """
    logger.info(f"Streaming transcription of: {audio_path}")

    # Load and resample to 16kHz
    audio, sr = librosa.load(audio_path, sr=16000)
    total_duration = len(audio) / sr

    logger.info(f"Audio duration: {total_duration:.2f}s, Sample rate: {sr}Hz")

    # Calculate chunk parameters
    chunk_samples = chunk_length * sr
    overlap_samples = overlap * sr
    stride = chunk_samples - overlap_samples

    # Process audio in chunks
    chunk_num = 0
    position = 0

    while position < len(audio):
        chunk_start_time = time.time()

        # Extract chunk
        chunk_end = min(position + chunk_samples, len(audio))
        audio_chunk = audio[position:chunk_end]

        # Pad if necessary (last chunk might be shorter)
        if len(audio_chunk) < chunk_samples:
            audio_chunk = np.pad(audio_chunk, (0, chunk_samples - len(audio_chunk)))

        # Process chunk
        inputs = processor(audio_chunk, sampling_rate=16000, return_tensors="pt")
        inputs = inputs.to(device)

        # Generate transcription for this chunk
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_features,
                language="en",
                task="transcribe",
                return_dict_in_generate=True
            )

        transcription = processor.batch_decode(outputs.sequences, skip_special_tokens=True)[0]

        chunk_end_time = time.time()
        processing_time = chunk_end_time - chunk_start_time

        # Calculate actual time boundaries in the audio
        start_sec = position / sr
        end_sec = min(chunk_end / sr, total_duration)

        chunk_num += 1

        logger.info(f"Chunk {chunk_num}: {start_sec:.2f}s - {end_sec:.2f}s (processed in {processing_time:.2f}s)")

        yield {
            'chunk_num': chunk_num,
            'text': transcription,
            'start_time': start_sec,
            'end_time': end_sec,
            'processing_time': processing_time
        }

        # Move to next chunk
        position += stride

        # Break if we've reached the end
        if chunk_end >= len(audio):
            break

def merge_chunks(chunks):
    """
    Merge overlapping chunks into a single transcription.
    Takes the first 75% of each chunk and 100% of the last chunk to avoid overlap issues.
    """
    if not chunks:
        return ""

    if len(chunks) == 1:
        return chunks[0]['text'].strip()

    merged_parts = []

    # For each chunk except the last, take first 75% of words
    for i in range(len(chunks) - 1):
        words = chunks[i]['text'].strip().split()
        cutoff = int(len(words) * 0.75)
        merged_parts.append(" ".join(words[:cutoff]))

    # Take the entire last chunk
    merged_parts.append(chunks[-1]['text'].strip())

    return " ".join(merged_parts)

# Test streaming transcription
print(f"\n{'='*70}")
print("STREAMING TRANSCRIPTION TEST")
print(f"{'='*70}\n")

overall_start = time.time()
chunks = []

for chunk_data in transcribe_streaming("../assets/call_1_calm.wav", chunk_length=5, overlap=1):
    chunks.append(chunk_data)

    # Display chunk as it arrives (simulating real-time display)
    print(f"\n[Chunk {chunk_data['chunk_num']}] ({chunk_data['start_time']:.1f}s - {chunk_data['end_time']:.1f}s)")
    print(f"├─ Text: {chunk_data['text']}")
    print(f"└─ Processing time: {chunk_data['processing_time']:.2f}s")

overall_end = time.time()

# Merge all chunks
final_transcription = merge_chunks(chunks)

print(f"\n{'='*70}")
print("FINAL MERGED TRANSCRIPTION")
print(f"{'='*70}")
print(final_transcription)
print(f"\n{'='*70}")
print(f"Total chunks: {len(chunks)}")
print(f"Time to first chunk: {chunks[0]['processing_time']:.2f}s")
print(f"Total processing time: {overall_end - overall_start:.2f}s")
print(f"Average chunk time: {np.mean([c['processing_time'] for c in chunks]):.2f}s")
print(f"{'='*70}")
