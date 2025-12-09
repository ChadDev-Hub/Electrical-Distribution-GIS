import React from 'react'
import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Mainmap from './components/map/mainmap'
import CssBaseline from '@mui/material/CssBaseline';
import HomePage from './homepage';
import DashBoard from './components/dashboard/dashboard';
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/homepage/' element={<HomePage />}>
          <Route path='map' element={<Mainmap />} />
          <Route path='dashboard' element={<DashBoard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
