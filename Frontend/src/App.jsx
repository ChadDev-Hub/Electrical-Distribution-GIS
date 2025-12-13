import React, {useState} from 'react'
import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Mainmap from './components/map/mainmap'
import HomePage from './homepage';
import DashBoard from './components/dashboard/dashboard';
import { useMediaQuery, CssBaseline } from '@mui/material';
import { WebSocketProvider } from './components/mapWebSocketProvider';
import { ThemeProvider, createTheme } from "@mui/material/styles";

function App() {
  const isMobile = useMediaQuery("(max-width: 768px)");
  const [darkMode, setDarkMode] = useState(true);
  const theme = createTheme({
    
      palette: {
        mode: darkMode ? "dark" : "light",
        primary: {
          main: darkMode ? "#90caf9" : "#1976d2",
        },
        background: {
          default: darkMode ? "#121212" : "#f4f6fb",
          paper: darkMode ? "#1a1a1c" : "#ffffff",
          box: darkMode ? "#1a1a1c" : "#ffffff",
        }
      },
      shape: { borderRadius: 16 },
      typography: { fontFamily: 'Roboto, sans-serif' },
    });

    const handleThemeSwitch = () => {
      setDarkMode(!darkMode)
    }
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline/>
      <WebSocketProvider>
      <BrowserRouter>
        <Routes>
          <Route path='/homepage/'  element={<HomePage darkMode={darkMode} switchTheme={handleThemeSwitch}  isMobile={isMobile}/>}>
            <Route path='map' element={<Mainmap darkMode={darkMode}  isMobile={isMobile}/>} />
            <Route path='dashboard' element={<DashBoard isMobile={isMobile}/>}/>
          </Route>
        </Routes>
      </BrowserRouter>
    </WebSocketProvider>
    </ThemeProvider>
  )
}

export default App
