import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import ProtectedPage from './protected.tsx';
import Login from './login.tsx';

const Index = () => {
    return (
        <Router>
    <Routes>
        <Route path= "/" element={<Login/>} />
        <Route path= "/protected" element={<ProtectedPage/>} />
    </Routes>
  </Router>
    );
}

export default Index;

