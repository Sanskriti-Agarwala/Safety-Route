import React, { useState, useEffect } from 'react';
import api from '../services/api';

const LocationSearch = ({ onLocationSelect, placeholder = "Search location..." }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }

    const delayDebounceFn = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await api.searchPlaces(query, 5);
        setResults(response.results || []);
        setShowResults(true);
      } catch (error) {
        console.error('Search failed:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  const handleSelect = (location) => {
    setQuery(location.name);
    setShowResults(false);
    onLocationSelect({
      latitude: location.latitude,
      longitude: location.longitude,
      address: location.name
    });
  };

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setShowResults(true)}
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '12px',
          fontSize: '16px',
          border: '1px solid #ddd',
          borderRadius: '8px',
        }}
      />

      {loading && (
        <div style={{ position: 'absolute', right: '12px', top: '12px' }}>
          ⏳
        </div>
      )}

      {showResults && results.length > 0 && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            backgroundColor: 'white',
            border: '1px solid #ddd',
            borderRadius: '8px',
            marginTop: '4px',
            maxHeight: '300px',
            overflowY: 'auto',
            zIndex: 1000,
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}
        >
          {results.map((result, idx) => (
            <div
              key={idx}
              onClick={() => handleSelect(result)}
              style={{
                padding: '12px',
                cursor: 'pointer',
                borderBottom: idx < results.length - 1 ? '1px solid #eee' : 'none',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#f3f4f6'}
              onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
            >
              {result.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LocationSearch;