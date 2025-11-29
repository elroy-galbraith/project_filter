import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Custom marker icons
const createMarkerIcon = (isDistress) => {
  const color = isDistress ? '#dc2626' : '#22c55e';
  const svg = `
    <svg width="32" height="42" viewBox="0 0 32 42" xmlns="http://www.w3.org/2000/svg">
      <path d="M16 0C7.2 0 0 7.2 0 16c0 13 16 26 16 26s16-13 16-26c0-8.8-7.2-16-16-16z"
            fill="${color}"
            stroke="#000"
            stroke-width="2"/>
      <circle cx="16" cy="16" r="6" fill="#fff"/>
    </svg>
  `;

  return L.divIcon({
    html: `<div class="${isDistress ? 'marker-pulse' : ''}">${svg}</div>`,
    className: 'custom-marker',
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -42]
  });
};

export default function MapView({ calls, selectedCall, onSelectCall }) {
  if (!calls || calls.length === 0) return null;

  // Center on Jamaica (St. Elizabeth Parish area)
  const center = [18.1, -77.9];

  return (
    <div className="map-container">
      <MapContainer
        center={center}
        zoom={10}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {calls.map((call) => (
          <Marker
            key={call.id}
            position={[call.lat, call.lng]}
            icon={createMarkerIcon(call.is_distress)}
            eventHandlers={{
              click: () => onSelectCall(call)
            }}
          >
            <Popup>
              <div className="map-popup">
                <div className="map-popup-header">
                  <strong>{call.id}</strong>
                  <span className={`popup-badge ${call.is_distress ? 'distress' : 'normal'}`}>
                    {call.is_distress ? '🚨 DISTRESS' : '✓ Normal'}
                  </span>
                </div>
                <div className="map-popup-time">{call.time}</div>
                <div className="map-popup-location">📍 {call.location}</div>
                <div className="map-popup-category">{call.category}</div>
                {call.nlp_extraction && (
                  <div className="map-popup-dispatch">
                    <strong>Dispatch:</strong> {call.nlp_extraction.resource_need || 'TBD'}
                  </div>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Map Legend */}
      <div className="map-legend">
        <div className="map-legend-title">CALL STATUS</div>
        <div className="map-legend-item">
          <div className="legend-marker distress"></div>
          <span>Distress (Human Review)</span>
        </div>
        <div className="map-legend-item">
          <div className="legend-marker normal"></div>
          <span>Normal (Auto-Logged)</span>
        </div>
      </div>
    </div>
  );
}
