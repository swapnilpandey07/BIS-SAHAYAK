import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Landing from './pages/Landing';
import Assistant from './pages/Assistant';
import Documents from './pages/Documents';
import DocumentDetail from './pages/DocumentDetail';
import Search from './pages/Search';
import Dashboard from './pages/Dashboard';
import HowItWorks from './pages/HowItWorks';

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />
        <main style={{ flex: 1, marginTop: 'var(--nav-height)' }}>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/chat" element={<Navigate to="/assistant" replace />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/documents/:id" element={<DocumentDetail />} />
            <Route path="/search" element={<Search />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/how-it-works" element={<HowItWorks />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
