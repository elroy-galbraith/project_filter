/**
 * LiveCall Component
 *
 * Provides live audio capture and real-time TRIDENT processing.
 *
 * Features:
 * - Microphone audio capture
 * - Real-time WebSocket streaming
 * - Live transcript updates
 * - Bio-acoustic visualization
 * - Triage status display
 */

import { useState, useCallback, useEffect } from 'react';
import useAudioRecorder from '../hooks/useAudioRecorder';
import useWebSocket from '../hooks/useWebSocket';

const LiveCall = () => {
  const [callState, setCallState] = useState('idle'); // idle, active, processing, ended
  const [callId, setCallId] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [bioAcoustic, setBioAcoustic] = useState(null);
  const [triage, setTriage] = useState(null);
  const [duration, setDuration] = useState(0);
  const [chunksReceived, setChunksReceived] = useState(0);
  const [error, setError] = useState(null);

  // WebSocket handler
  const handleWebSocketMessage = useCallback((data) => {
    console.log('WebSocket message:', data.type);

    switch (data.type) {
      case 'connected':
        setCallId(data.call_id);
        setCallState('active');
        console.log('Call started:', data.call_id);
        break;

      case 'buffer_update':
        setDuration(data.duration);
        setChunksReceived(data.chunks_received);
        break;

      case 'processing_started':
        setCallState('processing');
        break;

      case 'processing_complete':
        setTranscript(data.transcript);
        setConfidence(data.confidence);
        setBioAcoustic(data.bio_acoustic);
        setTriage(data.triage);
        setCallState('active');
        break;

      case 'error':
        setError(data.message);
        console.error('Processing error:', data.message);
        break;

      case 'call_ended':
        setCallState('ended');
        console.log('Call ended:', data.analysis);
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  }, []);

  // WebSocket connection
  const {
    connect: connectWS,
    disconnect: disconnectWS,
    sendAudio,
    connectionState,
    isConnected
  } = useWebSocket({
    url: 'ws://localhost:8000/ws/live',
    onMessage: handleWebSocketMessage,
    onError: (err) => {
      setError('WebSocket connection error');
      console.error('WebSocket error:', err);
    }
  });

  // Audio recorder
  const {
    startRecording,
    stopRecording,
    isRecording,
    error: recordingError
  } = useAudioRecorder({
    onAudioChunk: (audioBlob) => {
      // Send audio chunk to backend via WebSocket
      sendAudio(audioBlob);
    },
    chunkInterval: 1000 // Send 1-second chunks
  });

  // Start call
  const handleStartCall = useCallback(async () => {
    setError(null);
    setTranscript('');
    setConfidence(0);
    setBioAcoustic(null);
    setTriage(null);
    setDuration(0);
    setChunksReceived(0);

    // Connect WebSocket
    connectWS();

    // Wait a bit for WebSocket to connect, then start recording
    setTimeout(() => {
      startRecording();
    }, 500);
  }, [connectWS, startRecording]);

  // End call
  const handleEndCall = useCallback(() => {
    stopRecording();
    disconnectWS();
    setCallState('ended');
  }, [stopRecording, disconnectWS]);

  // Display recording error
  useEffect(() => {
    if (recordingError) {
      setError(recordingError);
    }
  }, [recordingError]);

  return (
    <div className="live-call-container">
      {/* Header */}
      <div className="live-call-header">
        <h2>🎙️ Live Call Processing</h2>
        {callId && (
          <div className="call-id">
            Call ID: <strong>{callId}</strong>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="live-call-controls">
        {callState === 'idle' && (
          <button
            className="btn-start-call"
            onClick={handleStartCall}
            disabled={connectionState === 'connecting'}
          >
            {connectionState === 'connecting' ? 'Connecting...' : '▶ Start Live Call'}
          </button>
        )}

        {(callState === 'active' || callState === 'processing') && (
          <div className="call-active-controls">
            <button
              className="btn-end-call"
              onClick={handleEndCall}
            >
              ⏹ End Call
            </button>
            <div className="recording-indicator">
              <div className="recording-dot"></div>
              <span>RECORDING</span>
            </div>
          </div>
        )}

        {callState === 'ended' && (
          <button
            className="btn-new-call"
            onClick={handleStartCall}
          >
            🔄 New Call
          </button>
        )}
      </div>

      {/* Status */}
      <div className="live-call-status">
        <div className="status-item">
          <span className="status-label">Connection:</span>
          <span className={`status-value status-${connectionState}`}>
            {connectionState.toUpperCase()}
          </span>
        </div>
        <div className="status-item">
          <span className="status-label">Duration:</span>
          <span className="status-value">{duration.toFixed(1)}s</span>
        </div>
        <div className="status-item">
          <span className="status-label">Chunks:</span>
          <span className="status-value">{chunksReceived}</span>
        </div>
        {callState === 'processing' && (
          <div className="status-item processing">
            <span className="spinner-small"></span>
            <span>Processing audio...</span>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="live-call-error">
          ⚠️ {error}
        </div>
      )}

      {/* Live Results */}
      {(callState === 'active' || callState === 'processing' || callState === 'ended') && (
        <div className="live-call-results">
          {/* Triage Status */}
          {triage && (
            <div className={`triage-status triage-${triage.queue}`}>
              <div className="triage-header">
                <div className="triage-queue">{triage.queue}</div>
                <div className="triage-priority">Priority {triage.priority_level}</div>
              </div>
              <div className="triage-action">
                {triage.dispatcher_action}
              </div>
            </div>
          )}

          {/* Transcript */}
          <div className="live-transcript">
            <h3>Live Transcript</h3>
            <div className="transcript-box">
              {transcript || <em>Waiting for speech...</em>}
            </div>
            {confidence > 0 && (
              <div className="confidence-indicator">
                Confidence: <strong>{(confidence * 100).toFixed(1)}%</strong>
              </div>
            )}
          </div>

          {/* Bio-Acoustic */}
          {bioAcoustic && (
            <div className="live-bioacoustic">
              <h3>Bio-Acoustic Analysis</h3>
              <div className="bio-metrics">
                <div className="bio-metric">
                  <span className="metric-label">F0 Mean:</span>
                  <span className="metric-value">{bioAcoustic.f0_mean.toFixed(1)} Hz</span>
                </div>
                <div className="bio-metric">
                  <span className="metric-label">Distress Score:</span>
                  <span className={`metric-value ${bioAcoustic.distress_score > 0.5 ? 'high-distress' : 'low-distress'}`}>
                    {(bioAcoustic.distress_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="bio-metric">
                  <span className="metric-label">Energy:</span>
                  <span className="metric-value">{(bioAcoustic.energy * 100).toFixed(1)}%</span>
                </div>
                <div className="bio-metric">
                  <span className="metric-label">Instability:</span>
                  <span className="metric-value">{(bioAcoustic.instability * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      {callState === 'idle' && (
        <div className="live-call-instructions">
          <h3>How to use Live Processing:</h3>
          <ol>
            <li>Click "Start Live Call" to begin recording</li>
            <li>Allow microphone access when prompted</li>
            <li>Speak naturally - the system will process your audio in real-time</li>
            <li>Watch the transcript and triage decision update live</li>
            <li>Click "End Call" when finished</li>
          </ol>
          <p className="note">
            <strong>Note:</strong> Processing occurs when silence is detected (1.5s pause).
            Results appear within 5-10 seconds of each utterance.
          </p>
        </div>
      )}
    </div>
  );
};

export default LiveCall;
