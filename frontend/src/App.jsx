import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import CallFeed from './components/CallFeed';
import NLPIntelRow from './components/NLPIntelRow';
import TranscriptCompact from './components/TranscriptCompact';
import BioAcousticCompact from './components/BioAcousticCompact';

function App() {
  const [calls, setCalls] = useState([]);
  const [selectedCall, setSelectedCall] = useState(null);
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);

  useEffect(() => {
    // Fetch calls on mount
    fetchCalls();
  }, []);

  const fetchCalls = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/calls');
      setCalls(response.data);
      // Select first call by default
      if (response.data.length > 0) {
        setSelectedCall(response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching calls:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCall = async (call) => {
    // Simulate loading delay like Streamlit spinner
    setSwitching(true);
    setTimeout(() => {
      setSelectedCall(call);
      setSwitching(false);
    }, 700);
  };

  const pendingReview = calls.filter(c => c.is_distress).length;

  if (loading) {
    return (
      <div className="app">
        <div className="loading-text">
          <div className="spinner"></div>
          Loading call data...
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Header */}
      <div className="brand-header">
        <div>
          <p className="brand-title">🚨 PROJECT FILTER</p>
          <p className="brand-subtitle">Crisis Triage Dashboard • Bio-Acoustic Intelligence</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <p className="brand-logo">SMG-Labs</p>
          <p className="brand-subtitle">Caribbean Voices AI</p>
        </div>
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <div>
          <strong>Active Region:</strong> St. Elizabeth Parish, Jamaica
        </div>
        <div>
          <span className="status-active">● HURRICANE MELISSA - DISASTER MODE</span>
        </div>
        <div>
          <strong>Pending Human Review:</strong> {pendingReview}
        </div>
      </div>

      <hr />

      {/* Main Layout */}
      <div className="layout">
        {/* Sidebar */}
        <div className="sidebar">
          <CallFeed
            calls={calls}
            selectedCall={selectedCall}
            onSelectCall={handleSelectCall}
            loading={switching}
          />
        </div>

        {/* Main Content - Zero Scroll Layout */}
        <div className="main-content">
          {switching ? (
            <div className="loading-text">
              <div className="spinner"></div>
              Analyzing audio stream...
            </div>
          ) : (
            <>
              {/* NLP Intel Row - Dispatch-Critical Data (Top Priority) */}
              <NLPIntelRow call={selectedCall} />

              {/* Evidence Row - Supporting Information */}
              <div className="evidence-row">
                <TranscriptCompact call={selectedCall} />
                <BioAcousticCompact call={selectedCall} />
              </div>
            </>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        Project Filter • SMG-Labs • Caribbean Voices AI Hackathon 2025 • Hurricane Melissa Response Demo
      </div>
    </div>
  );
}

export default App;
