import React from 'react'
import './App.css'
import {BrowserRouter, Route, Routes} from 'react-router-dom'
import Mainmap from './components/map/mainmap'
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import HomePage from './homepage';

function App() {
  return (
    <HomePage/>
      
  )
}

export default App
