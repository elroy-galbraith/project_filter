"""
Comparison: Batch vs Streaming Transcription

This script compares the performance and user experience of:
1. Batch processing (process entire audio at once)
2. Streaming processing (process in chunks)
"""

from transformers import WhisperProcessor, WhisperForConditionalGeneration
from peft import PeftModel
import torch
import librosa
import logging
import time
import numpy as np

# Initialize logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise
logger = logging.getLogger(__name__)

# Load model (shared for both approaches)
base_model_name = "openai/whisper-large-v3"
adapter_path = "./model_full"

print("Loading model...")
model = WhisperForConditionalGeneration.from_pretrained(base_model_name)
model = PeftModel.from_pretrained(model, adapter_path)
processor = WhisperProcessor.from_pretrained(base_model_name)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print(f"Model loaded on {device}\n")

# ============================================================================
# BATCH PROCESSING
# ============================================================================

def transcribe_batch(audio_path):
    """Traditional batch processing - entire audio at once"""
    audio, sr = librosa.load(audio_path, sr=16000)
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt")
    inputs = inputs.to(device)

    with torch.no_grad():
        outputs = model.generate(
            inputs.input_features,
            language="en",
            task="transcribe",
            return_dict_in_generate=True
        )

    return processor.batch_decode(outputs.sequences, skip_special_tokens=True)[0]

# ============================================================================
# STREAMING PROCESSING
# ============================================================================

def transcribe_streaming(audio_path, chunk_length=5, overlap=1):
    """Streaming processing - chunks with overlap"""
    audio, sr = librosa.load(audio_path, sr=16000)

    chunk_samples = chunk_length * sr
    overlap_samples = overlap * sr
    stride = chunk_samples - overlap_samples

    chunks = []
    position = 0

    while position < len(audio):
        chunk_end = min(position + chunk_samples, len(audio))
        audio_chunk = audio[position:chunk_end]

        if len(audio_chunk) < chunk_samples:
            audio_chunk = np.pad(audio_chunk, (0, chunk_samples - len(audio_chunk)))

        inputs = processor(audio_chunk, sampling_rate=16000, return_tensors="pt")
        inputs = inputs.to(device)

        with torch.no_grad():
            outputs = model.generate(
                inputs.input_features,
                language="en",
                task="transcribe",
                return_dict_in_generate=True
            )

        transcription = processor.batch_decode(outputs.sequences, skip_special_tokens=True)[0]
        chunks.append(transcription.strip())

        yield transcription.strip()

        position += stride
        if chunk_end >= len(audio):
            break

def merge_streaming_chunks(chunks):
    """Merge chunks using 75% rule"""
    if len(chunks) == 1:
        return chunks[0]

    merged_parts = []
    for i in range(len(chunks) - 1):
        words = chunks[i].split()
        cutoff = int(len(words) * 0.75)
        merged_parts.append(" ".join(words[:cutoff]))

    merged_parts.append(chunks[-1])
    return " ".join(merged_parts)

# ============================================================================
# COMPARISON TEST
# ============================================================================

test_file = "../assets/call_1_calm.wav"

print("="*80)
print("COMPARISON: BATCH vs STREAMING TRANSCRIPTION")
print("="*80)

# Get audio duration
audio, sr = librosa.load(test_file, sr=16000)
duration = len(audio) / sr
print(f"\nTest file: {test_file}")
print(f"Audio duration: {duration:.2f} seconds\n")

# ============================================================================
print("-" * 80)
print("APPROACH 1: BATCH PROCESSING (Traditional)")
print("-" * 80)

batch_start = time.time()
batch_result = transcribe_batch(test_file)
batch_end = time.time()

print(f"⏱️  Time to first word: {batch_end - batch_start:.2f}s")
print(f"⏱️  Total processing time: {batch_end - batch_start:.2f}s")
print(f"📝 Transcription:\n   {batch_result}\n")

# ============================================================================
print("-" * 80)
print("APPROACH 2: STREAMING PROCESSING (Chunked)")
print("-" * 80)

streaming_start = time.time()
chunks = []
first_chunk_time = None

for i, chunk_text in enumerate(transcribe_streaming(test_file, chunk_length=5, overlap=1), 1):
    chunk_time = time.time()
    if first_chunk_time is None:
        first_chunk_time = chunk_time - streaming_start

    chunks.append(chunk_text)
    print(f"🔄 Chunk {i} received at {chunk_time - streaming_start:.2f}s: {chunk_text[:50]}...")

streaming_end = time.time()
merged_result = merge_streaming_chunks(chunks)

print(f"\n⏱️  Time to first word: {first_chunk_time:.2f}s ⚡ ({((batch_end - batch_start) / first_chunk_time):.1f}x faster)")
print(f"⏱️  Total processing time: {streaming_end - streaming_start:.2f}s")
print(f"📝 Merged transcription:\n   {merged_result}\n")

# ============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"""
┌─────────────────────────────────────────────────────────────────┐
│ METRIC                    │ BATCH        │ STREAMING           │
├───────────────────────────┼──────────────┼─────────────────────┤
│ Time to first word        │ {batch_end - batch_start:6.2f}s      │ {first_chunk_time:6.2f}s ⚡        │
│ Total processing time     │ {batch_end - batch_start:6.2f}s      │ {streaming_end - streaming_start:6.2f}s            │
│ Chunks processed          │ 1            │ {len(chunks)}                   │
│ User experience           │ Wait for all │ Progressive results │
└───────────────────────────┴──────────────┴─────────────────────┘

KEY INSIGHTS:
✅ Streaming provides {((batch_end - batch_start) / first_chunk_time):.1f}x faster time-to-first-word
✅ Users can start reading transcription {first_chunk_time:.1f}s earlier
✅ Better for real-time/emergency scenarios where immediate feedback matters
⚠️  Total processing takes slightly longer due to overlap
⚠️  Accuracy may vary slightly at chunk boundaries

RECOMMENDATION FOR EMERGENCY CALLS:
Use streaming for live calls where operators need immediate context.
Use batch for offline processing of recorded calls for maximum accuracy.
""")

print("=" * 80)
