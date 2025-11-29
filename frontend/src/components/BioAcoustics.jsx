export default function BioAcoustics({ call }) {
  if (!call) return null;

  const pitchHigh = call.pitch_avg > 240;
  const energyHigh = call.energy_avg > 0.05;

  return (
    <div className="content-section">
      <h3>📈 Bio-Acoustic Analysis</h3>
      <p className="section-caption">Domain-calibrated for Caribbean vocal patterns</p>

      <div className="distress-meter">
        <h4>Vocal Distress Severity</h4>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${call.distress_score}%` }}
          />
        </div>
      </div>

      <div className="acoustic-metrics">
        <div className="acoustic-metric">
          <h4>Avg Pitch</h4>
          <div className="acoustic-value">{call.pitch_avg} Hz</div>
          <div className={`acoustic-delta ${pitchHigh ? 'high' : 'normal'}`}>
            {pitchHigh ? 'High' : 'Normal'}
          </div>
          <div className="acoustic-help">
            Baseline: 100-180Hz. Values &gt;240Hz indicate vocal stress/panic.
          </div>
        </div>

        <div className="acoustic-metric">
          <h4>Energy (RMS)</h4>
          <div className="acoustic-value">{call.energy_avg.toFixed(3)}</div>
          <div className={`acoustic-delta ${energyHigh ? 'high' : 'normal'}`}>
            {energyHigh ? 'High' : 'Normal'}
          </div>
          <div className="acoustic-help">
            Baseline: 0.02-0.04. High values indicate shouting or loud environment.
          </div>
        </div>
      </div>

      <hr />

      <h3>🤖 System Decision</h3>

      {call.is_distress ? (
        <div className="decision-box red">
          <h3>🚨 PRIORITY ROUTING</h3>
          <p>
            <strong>Trigger:</strong> Bio-Acoustic Distress (Score: {call.distress_score}) +
            Low ASR Confidence ({Math.round(call.confidence * 100)}%)
          </p>
          <p><strong>Action:</strong> Immediate routing to Human Dispatcher</p>
          <p><strong>Queue Position:</strong> #1 (Priority Override)</p>
        </div>
      ) : (
        <div className="decision-box green">
          <h3>✅ AUTO-LOGGED</h3>
          <p><strong>Trigger:</strong> Standard dialect + Calm vocal signature</p>
          <p><strong>Action:</strong> Logged to Infrastructure Incident Database</p>
          <p><strong>Category:</strong> {call.category}</p>
        </div>
      )}
    </div>
  );
}
