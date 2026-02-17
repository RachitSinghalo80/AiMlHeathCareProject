import React from 'react';
import { Layout } from './components/layout';

function App() {
  return (
    <Layout>
      <div style={{ padding: 50, textAlign: 'center' }}>
        <h1>Layout Check</h1>
        <p style={{ color: 'green', fontWeight: 'bold' }}>
          If you can see this, Layout is working!
        </p>
      </div>
    </Layout>
  );
}

export default App;
