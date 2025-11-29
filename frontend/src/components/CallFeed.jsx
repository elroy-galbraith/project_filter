export default function CallFeed({ calls, selectedCall, onSelectCall, loading }) {
  return (
    <div className="call-feed">
      <h2>📡 Incoming Call Feed</h2>
      <p className="call-feed-caption">Click to inspect call details</p>
      <hr />

      {calls.map(call => {
        const icon = call.is_distress ? "🔴" : "🟢";
        const status = call.is_distress ? "HUMAN" : "AUTO";
        const isSelected = selectedCall?.id === call.id;
        const distressClass = call.is_distress ? "distress" : "normal";

        return (
          <button
            key={call.id}
            className={`call-button ${isSelected ? 'primary' : ''} ${distressClass}`}
            onClick={() => onSelectCall(call)}
            disabled={loading}
          >
            {icon} {call.time} | {status}
          </button>
        );
      })}

      <hr />
      <div className="feed-legend">
        <div>🟢 Auto-logged to Infrastructure DB</div>
        <div>🔴 Routed to Human Dispatcher</div>
      </div>
    </div>
  );
}
