import React from 'react'
import './App.css'
import {BrowserRouter, Route, Routes} from 'react-router-dom'
import Mainmap from './components/map/mainmap'
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';


const  darkTheme = createTheme({
  palette: {
    mode:"light",
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline/>
      <main>This app is using the dark mode</main>
      <Mainmap/>
    </ThemeProvider>
      
  )
}

export default App
