export default function NLPIntelRow({ call }) {
  if (!call || !call.nlp_extraction) return null;

  const nlp = call.nlp_extraction;
  const isDistress = call.is_distress;

  return (
    <div className="intel-row">
      {/* Location Intel */}
      <div className={`intel-card ${isDistress ? 'urgent' : 'normal'}`}>
        <h4 className="intel-header">📍 LOCATION</h4>
        <div className="intel-primary">{nlp.location || 'Unknown'}</div>
        {nlp.landmark && (
          <div className="intel-secondary">📌 {nlp.landmark}</div>
        )}
        {nlp.blocked_access && (
          <div className="intel-warning">🚧 {nlp.blocked_access}</div>
        )}
      </div>

      {/* Hazard Assessment */}
      <div className={`intel-card ${isDistress ? 'urgent' : 'normal'}`}>
        <h4 className="intel-header">⚠️ HAZARD</h4>
        <div className="intel-primary">{nlp.hazard_type || 'Unknown'}</div>
        {nlp.people_count && (
          <div className="intel-people">👥 {nlp.people_count}</div>
        )}
      </div>

      {/* Resource Dispatch */}
      <div className={`intel-card intel-card-dispatch ${isDistress ? 'urgent' : 'normal'}`}>
        <h4 className="intel-header">🆘 DISPATCH</h4>
        <div className="intel-primary">{nlp.resource_need || 'TBD'}</div>
      </div>
    </div>
  );
}
