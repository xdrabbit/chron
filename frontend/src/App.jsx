import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './pages/Home';
import AddEvent from './pages/AddEvent';

function App() {
    return (
        <Router>
            <div className="min-h-screen bg-slate-900 text-slate-100">
                <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/add" element={<AddEvent />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
