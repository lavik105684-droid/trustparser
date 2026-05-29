import React from 'react';
import OfficeGrid from './components/OfficeGrid';

export default function App() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px', boxSizing: 'border-box' }}>
      <OfficeGrid />
    </div>
  );
}

