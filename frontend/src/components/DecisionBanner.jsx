export default function DecisionBanner({ call }) {
  if (!call) return null;

  const isDistress = call.is_distress;

  return (
    <div className={`decision-banner ${isDistress ? 'urgent' : 'normal'}`}>
      {isDistress ? (
        <>
          <div className="decision-icon">🚨</div>
          <div className="decision-content">
            <h2 className="decision-title">PRIORITY ROUTING</h2>
            <div className="decision-details">
              <span className="decision-badge">Queue #1 (Priority Override)</span>
              <span className="decision-trigger">
                Trigger: Bio-Acoustic Distress ({call.distress_score}) + Low ASR Confidence ({Math.round(call.confidence * 100)}%)
              </span>
            </div>
            <div className="decision-action">
              <strong>Action:</strong> Immediate routing to Human Dispatcher
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="decision-icon">✅</div>
          <div className="decision-content">
            <h2 className="decision-title">AUTO-LOGGED</h2>
            <div className="decision-details">
              <span className="decision-badge">Infrastructure Database</span>
              <span className="decision-trigger">
                Trigger: Standard dialect + Calm vocal signature
              </span>
            </div>
            <div className="decision-action">
              <strong>Category:</strong> {call.category}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
