/**
 * useAudioRecorder Hook
 *
 * Provides microphone audio recording with MediaRecorder API.
 * Captures audio chunks and provides them via callback for streaming.
 *
 * Features:
 * - Microphone access and permission handling
 * - Audio chunk streaming (configurable interval)
 * - Start/stop recording controls
 * - Error handling
 *
 * Usage:
 *   const { startRecording, stopRecording, isRecording, error } = useAudioRecorder({
 *     onAudioChunk: (blob) => {
 *       // Send blob via WebSocket
 *       ws.send(blob);
 *     },
 *     chunkInterval: 1000 // 1 second chunks
 *   });
 */

import { useState, useRef, useCallback } from 'react';

export const useAudioRecorder = ({ onAudioChunk, chunkInterval = 1000 }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const mediaStreamRef = useRef(null);

  const startRecording = useCallback(async () => {
    try {
      setError(null);

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1, // Mono
          sampleRate: 16000, // 16kHz for Whisper
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      mediaStreamRef.current = stream;

      // Create MediaRecorder
      // Try WebM Opus first (best compression), fallback to browser default
      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/webm';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          mimeType = ''; // Use browser default
        }
      }

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: mimeType || undefined,
        audioBitsPerSecond: 128000 // 128 kbps
      });

      mediaRecorderRef.current = mediaRecorder;

      // Handle audio chunks
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          onAudioChunk(event.data);
        }
      };

      // Handle recording errors
      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event.error);
        setError(event.error?.message || 'Recording error');
        stopRecording();
      };

      // Start recording with chunk interval
      mediaRecorder.start(chunkInterval);
      setIsRecording(true);

      console.log(`Recording started with ${mimeType || 'default'} codec`);

    } catch (err) {
      console.error('Error starting recording:', err);
      setError(err.message || 'Failed to access microphone');
      setIsRecording(false);
    }
  }, [onAudioChunk, chunkInterval]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }

    setIsRecording(false);
    console.log('Recording stopped');
  }, []);

  return {
    startRecording,
    stopRecording,
    isRecording,
    error
  };
};

export default useAudioRecorder;
