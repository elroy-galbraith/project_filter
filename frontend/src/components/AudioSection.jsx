export default function AudioSection({ call }) {
  if (!call) return null;

  return (
    <div className="content-section">
      <h3>🎧 Audio Source</h3>
      <audio controls src={`/${call.audio_file}`} />

      <h3>📝 ASR Transcription</h3>
      <p className="section-caption">Model: Whisper-Caribbean (Fine-tuned)</p>

      <div className={`transcript-box ${call.is_distress ? 'error' : 'success'}`}>
        {call.transcript}

        {call.is_distress ? (
          <div className="transcript-warning">
            ⚠️ <strong>Low Confidence Warning:</strong> Transcript likely incomplete.
            Deep dialect and/or acoustic interference detected.
          </div>
        ) : (
          <div className="transcript-success">
            ✅ High confidence transcription. Auto-logged to incident database.
          </div>
        )}
      </div>

      <div className="location-text">Detected Location: {call.location}</div>
    </div>
  );
}
