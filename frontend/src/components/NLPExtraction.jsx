export default function NLPExtraction({ call }) {
  if (!call || !call.nlp_extraction) return null;

  const nlp = call.nlp_extraction;
  const isDistress = call.is_distress;

  return (
    <div className="nlp-section">
      <h3>🧠 Local NLP Extraction</h3>
      <p className="section-caption">
        Entity extraction via Llama-3-8B (Offline via Ollama) • Enabled by accurate Caribbean ASR
      </p>

      <div className="nlp-grid">
        {/* Location Intel */}
        <div className="nlp-column">
          <h4>📍 Location Intel</h4>
          <div className="nlp-card info">
            <strong>Location:</strong> {nlp.location || 'N/A'}
          </div>
          {nlp.landmark && (
            <div className="nlp-card info">
              <strong>Landmark:</strong> {nlp.landmark}
            </div>
          )}
          {nlp.blocked_access && (
            <div className="nlp-card warning">
              <strong>Access:</strong> {nlp.blocked_access}
            </div>
          )}
        </div>

        {/* Hazard Assessment */}
        <div className="nlp-column">
          <h4>⚠️ Hazard Assessment</h4>
          <div className={`nlp-card ${isDistress ? 'error' : 'warning'}`}>
            <strong>Type:</strong> {nlp.hazard_type || 'N/A'}
          </div>
          {nlp.people_count && (
            <div className={`nlp-card ${isDistress ? 'error' : 'info'}`}>
              <strong>People:</strong> {nlp.people_count}
            </div>
          )}
        </div>

        {/* Resource Dispatch */}
        <div className="nlp-column">
          <h4>🆘 Resource Dispatch</h4>
          <div className={`nlp-card ${isDistress ? 'error' : 'success'}`}>
            <strong>{isDistress ? 'Need' : 'Assign'}:</strong> {nlp.resource_need || 'N/A'}
          </div>
        </div>
      </div>
    </div>
  );
}
