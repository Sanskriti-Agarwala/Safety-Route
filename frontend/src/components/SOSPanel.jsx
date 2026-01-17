import { useState } from 'react';
import api from '../services/api';

function SOSPanel() {
  const [contacts, setContacts] = useState(['']);
  const [message, setMessage] = useState('');
  const [triggering, setTriggering] = useState(false);
  const [result, setResult] = useState(null);

  const addContact = () => {
    setContacts([...contacts, '']);
  };

  const updateContact = (index, value) => {
    const newContacts = [...contacts];
    newContacts[index] = value;
    setContacts(newContacts);
  };

  const removeContact = (index) => {
    setContacts(contacts.filter((_, i) => i !== index));
  };

  const triggerSOS = async () => {
    if (contacts.filter(c => c.trim()).length === 0) {
      alert('Please add at least one emergency contact');
      return;
    }

    setTriggering(true);

    try {
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });

      const response = await api.triggerSOS(
        {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        },
        contacts.filter(c => c.trim()),
        message || null
      );

      setResult(response);
    } catch (err) {
      alert('Failed to trigger SOS: ' + err.message);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div style={{ padding: '40px 20px' }}>
      <div style={{ maxWidth: '600px', margin: '0 auto', background: 'white', borderRadius: '16px', padding: '40px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '64px', marginBottom: '16px' }}>🚨</div>
          <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '8px' }}>
            Emergency SOS
          </h2>
          <p style={{ color: '#6b7280' }}>
            Send instant alerts to your emergency contacts
          </p>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
            Emergency Contacts
          </label>
          {contacts.map((contact, index) => (
            <div key={index} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
              <input
                type="text"
                placeholder="Phone number or email"
                value={contact}
                onChange={(e) => updateContact(index, e.target.value)}
                style={{ flex: 1, padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px' }}
              />
              {contacts.length > 1 && (
                <button
                  onClick={() => removeContact(index)}
                  style={{
                    padding: '12px 16px',
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            onClick={addContact}
            style={{
              padding: '10px 20px',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            + Add Contact
          </button>
        </div>

        <div style={{ marginBottom: '32px' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
            Custom Message (Optional)
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Additional information about the emergency..."
            rows="3"
            style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontFamily: 'inherit' }}
          />
        </div>

        <button
          onClick={triggerSOS}
          disabled={triggering}
          style={{
            width: '100%',
            padding: '20px',
            background: triggering ? '#9ca3af' : '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            fontSize: '18px',
            fontWeight: '700',
            cursor: triggering ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 20px rgba(239, 68, 68, 0.4)'
          }}
        >
          {triggering ? 'SENDING SOS...' : '🚨 TRIGGER SOS'}
        </button>

        {result && (
          <div style={{ marginTop: '24px', padding: '20px', background: '#d1fae5', borderRadius: '12px' }}>
            <p style={{ color: '#065f46', fontWeight: '700', marginBottom: '8px' }}>
              ✅ SOS Alert Sent Successfully
            </p>
            <p style={{ color: '#047857', fontSize: '14px' }}>
              {result.message}
            </p>
            <p style={{ color: '#047857', fontSize: '12px', marginTop: '8px' }}>
              Alert ID: {result.sos_id}
            </p>
          </div>
        )}

        <div style={{ marginTop: '24px', padding: '16px', background: '#fef3c7', borderRadius: '8px', border: '2px solid #fbbf24' }}>
          <p style={{ color: '#92400e', fontSize: '14px', lineHeight: '1.6' }}>
            ⚠️ <strong>Note:</strong> This will share your current location with all emergency contacts. 
            Only use in genuine emergency situations.
          </p>
        </div>
      </div>
    </div>
  );
}

export default SOSPanel;