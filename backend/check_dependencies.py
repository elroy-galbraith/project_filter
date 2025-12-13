#!/usr/bin/env python3
"""
TRIDENT Dependency Checker

Verifies that all required dependencies are installed and configured correctly
for live audio processing.
"""

import sys
import subprocess


def check_python_packages():
    """Check required Python packages."""
    print("Checking Python packages...")

    required = {
        'fastapi': 'FastAPI web framework',
        'librosa': 'Audio processing library',
        'soundfile': 'Audio file I/O',
        'numpy': 'Numerical computing',
        'torch': 'PyTorch for Whisper',
        'transformers': 'Hugging Face transformers',
        'peft': 'PEFT for LoRA adapters'
    }

    optional = {
        'pydub': 'Audio format conversion (WebM fallback only)'
    }

    missing = []

    for package, description in required.items():
        try:
            __import__(package)
            print(f"  ✓ {package:20s} - {description}")
        except ImportError:
            print(f"  ✗ {package:20s} - MISSING")
            missing.append(package)

    print("\nOptional packages:")
    for package, description in optional.items():
        try:
            __import__(package)
            print(f"  ✓ {package:20s} - {description}")
        except ImportError:
            print(f"  ⚠ {package:20s} - Not installed (only needed for WebM fallback)")

    return len(missing) == 0


def check_ffmpeg():
    """Check if ffmpeg is installed (required for WebM/Opus decoding)."""
    print("\nChecking ffmpeg (required for WebM audio)...")

    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  ✓ ffmpeg installed: {version_line}")
            return True
        else:
            print("  ✗ ffmpeg not working properly")
            return False

    except FileNotFoundError:
        print("  ✗ ffmpeg NOT FOUND")
        print("\n  Installation instructions:")
        print("    macOS:   brew install ffmpeg")
        print("    Ubuntu:  sudo apt-get install ffmpeg")
        print("    Windows: Download from https://ffmpeg.org/download.html")
        return False
    except subprocess.TimeoutExpired:
        print("  ⚠ ffmpeg check timed out")
        return False


def check_whisper_model():
    """Check if Whisper model files exist."""
    print("\nChecking Whisper model...")

    import os
    model_path = "./model_full"

    if os.path.exists(model_path):
        required_files = [
            'adapter_config.json',
            'adapter_model.safetensors'
        ]

        missing = []
        for file in required_files:
            file_path = os.path.join(model_path, file)
            if os.path.exists(file_path):
                print(f"  ✓ {file}")
            else:
                print(f"  ✗ {file} - MISSING")
                missing.append(file)

        if len(missing) == 0:
            print(f"  ✓ LoRA adapter ready at {model_path}")
            return True
        else:
            print(f"  ⚠ Some model files missing")
            return False
    else:
        print(f"  ⚠ Model directory not found: {model_path}")
        print("     Will use base Whisper model (no LoRA adapter)")
        return True  # Not critical, base model works


def check_gpu():
    """Check GPU availability."""
    print("\nChecking GPU acceleration...")

    try:
        import torch

        if torch.cuda.is_available():
            print(f"  ✓ CUDA available: {torch.cuda.get_device_name(0)}")
            return True
        elif torch.backends.mps.is_available():
            print(f"  ✓ MPS (Apple Silicon) available")
            return True
        else:
            print(f"  ⚠ No GPU detected - will use CPU (slower)")
            return True  # Not critical, CPU works

    except Exception as e:
        print(f"  ✗ Error checking GPU: {e}")
        return False


def test_audio_processing():
    """Test basic audio processing."""
    print("\nTesting audio processing...")

    try:
        import librosa
        import numpy as np
        import tempfile
        import soundfile as sf

        # Create a simple test audio (1 second of sine wave at 440Hz)
        sr = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)

        # Test saving and loading
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            sf.write(tmp.name, audio, sr)

            # Try to load it back
            loaded, loaded_sr = librosa.load(tmp.name, sr=sr, mono=True)

            import os
            os.unlink(tmp.name)

        if len(loaded) > 0 and loaded_sr == sr:
            print(f"  ✓ Audio processing working")
            return True
        else:
            print(f"  ✗ Audio processing test failed")
            return False

    except Exception as e:
        print(f"  ✗ Audio processing error: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("TRIDENT Dependency Checker")
    print("=" * 60)

    results = {
        'Python packages': check_python_packages(),
        'ffmpeg': check_ffmpeg(),
        'Whisper model': check_whisper_model(),
        'GPU': check_gpu(),
        'Audio processing': test_audio_processing()
    }

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    all_critical_passed = True

    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"

        # Mark non-critical checks
        if check in ['GPU', 'Whisper model']:
            if not passed:
                status = "⚠ WARNING (non-critical)"
        elif not passed:
            all_critical_passed = False

        print(f"  {check:20s}: {status}")

    print("\n" + "=" * 60)

    if all_critical_passed:
        print("✓ All critical dependencies are ready!")
        print("\nYou can now run:")
        print("  uvicorn main:app --reload --port 8000")
        return 0
    else:
        print("✗ Some critical dependencies are missing.")
        print("\nPlease install missing dependencies before running TRIDENT.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
