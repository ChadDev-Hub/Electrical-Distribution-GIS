import React from 'react'
import './App.css'
import {BrowserRouter, Route, Routes} from 'react-router-dom'
import Mainmap from './components/map/mainmap'
import CssBaseline from '@mui/material/CssBaseline';
import HomePage from './homepage';

function App() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path='/Map' element={<HomePage/>}/>
    </Routes>
    </BrowserRouter>
  )
}

export default App
