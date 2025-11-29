export default function CallMetrics({ call }) {
  if (!call) return null;

  const confidence = Math.round(call.confidence * 100);
  const isDangerous = call.distress_score > 60;

  return (
    <div className="metrics-row">
      <div className="metric-card">
        <div className="metric-label">Call ID</div>
        <div className="metric-value">{call.id}</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Timestamp</div>
        <div className="metric-value">{call.time}</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">ASR Confidence</div>
        <div className="metric-value">{confidence}%</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Distress Score</div>
        <div className="metric-value">{call.distress_score}/100</div>
        {call.distress_score > 0 && (
          <div className={`metric-delta ${isDangerous ? 'critical' : 'normal'}`}>
            {isDangerous ? 'CRITICAL' : 'Normal'}
          </div>
        )}
      </div>

      <div className="metric-card">
        <div className="metric-label">Category</div>
        <div className="metric-value" style={{fontSize: '1rem'}}>{call.category}</div>
      </div>
    </div>
  );
}
