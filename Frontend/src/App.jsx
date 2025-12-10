import React from 'react'
import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Mainmap from './components/map/mainmap'
import CssBaseline from '@mui/material/CssBaseline';
import HomePage from './homepage';
import DashBoard from './components/dashboard/dashboard';

import { WebSocketProvider } from './components/mapWebSocketProvider';
function App() {
  return (
    <WebSocketProvider>
      <BrowserRouter>
        <Routes>
          <Route path='/homepage/' element={<HomePage />}>
            <Route path='map' element={<Mainmap/>} />
            <Route path='dashboard' element={<DashBoard />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </WebSocketProvider>

  )
}

export default App
