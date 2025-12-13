/**
 * useAudioRecorder Hook
 *
 * Provides microphone audio recording with Web Audio API.
 * Captures raw PCM audio samples and provides them via callback for streaming.
 *
 * Features:
 * - Microphone access and permission handling
 * - Raw PCM audio chunk streaming (16kHz, mono, float32)
 * - Start/stop recording controls
 * - Error handling
 *
 * Usage:
 *   const { startRecording, stopRecording, isRecording, error } = useAudioRecorder({
 *     onAudioChunk: (arrayBuffer) => {
 *       // Send raw PCM audio via WebSocket
 *       ws.send(arrayBuffer);
 *     },
 *     chunkInterval: 1000 // 1 second chunks
 *   });
 */

import { useState, useRef, useCallback } from 'react';

export const useAudioRecorder = ({ onAudioChunk, chunkInterval = 1000 }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);

  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const processorRef = useRef(null);
  const sourceRef = useRef(null);
  const audioBufferRef = useRef([]);
  const intervalRef = useRef(null);

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

      // Create audio context with 16kHz sample rate
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000
      });
      audioContextRef.current = audioContext;

      // Create media stream source
      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;

      // Create script processor for raw audio capture
      // Buffer size: 4096 samples = ~256ms at 16kHz
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      // Collect audio samples
      processor.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0);
        // Copy to avoid detached buffer issues
        const audioChunk = new Float32Array(inputData);
        audioBufferRef.current.push(audioChunk);
      };

      // Connect audio graph
      source.connect(processor);
      processor.connect(audioContext.destination);

      // Set up interval to send chunks
      intervalRef.current = setInterval(() => {
        if (audioBufferRef.current.length > 0) {
          // Concatenate all buffered chunks
          const totalLength = audioBufferRef.current.reduce((sum, chunk) => sum + chunk.length, 0);
          const combinedBuffer = new Float32Array(totalLength);

          let offset = 0;
          for (const chunk of audioBufferRef.current) {
            combinedBuffer.set(chunk, offset);
            offset += chunk.length;
          }

          // Clear buffer
          audioBufferRef.current = [];

          // Send as ArrayBuffer
          onAudioChunk(combinedBuffer.buffer);
        }
      }, chunkInterval);

      setIsRecording(true);
      console.log(`Recording started with Web Audio API (16kHz, mono, Float32)`);

    } catch (err) {
      console.error('Error starting recording:', err);
      setError(err.message || 'Failed to access microphone');
      setIsRecording(false);
    }
  }, [onAudioChunk, chunkInterval]);

  const stopRecording = useCallback(() => {
    // Clear interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Disconnect audio nodes
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Stop media stream
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    // Clear buffer
    audioBufferRef.current = [];

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
