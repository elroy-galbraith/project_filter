export default function BioAcousticCompact({ call }) {
  if (!call) return null;

  const pitchHigh = call.pitch_avg > 240;
  const energyHigh = call.energy_avg > 0.05;

  return (
    <div className="bioacoustic-compact">
      <h4 className="compact-header">📈 BIO-ACOUSTICS</h4>

      {/* Distress Meter */}
      <div className="distress-meter-compact">
        <div className="meter-header">
          <span>Vocal Distress</span>
          <span className="meter-value">{call.distress_score}/100</span>
        </div>
        <div className="progress-bar-compact">
          <div
            className="progress-fill-compact"
            style={{ width: `${call.distress_score}%` }}
          />
        </div>
      </div>

      {/* Acoustic Badges */}
      <div className="acoustic-badges">
        <div className={`badge-item ${pitchHigh ? 'high' : 'normal'}`}>
          <span className="badge-label">Pitch</span>
          <span className="badge-value">{call.pitch_avg} Hz</span>
          <span className="badge-status">{pitchHigh ? 'HIGH' : 'NORMAL'}</span>
        </div>

        <div className={`badge-item ${energyHigh ? 'high' : 'normal'}`}>
          <span className="badge-label">Energy</span>
          <span className="badge-value">{call.energy_avg.toFixed(3)}</span>
          <span className="badge-status">{energyHigh ? 'HIGH' : 'NORMAL'}</span>
        </div>
      </div>

      <div className="bioacoustic-note">
        Domain-calibrated for Caribbean vocal patterns
      </div>
    </div>
  );
}
