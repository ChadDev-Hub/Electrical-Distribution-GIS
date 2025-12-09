import React, { useState } from "react";
import Mainmap from "./components/map/mainmap";
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Drawer,
  Box,
  CssBaseline,
  useMediaQuery,
  Divider,
  List,
  ListItemButton,
  ListItemText
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { ThemeProvider, createTheme } from "@mui/material/styles";
function HomePage() {
  const [open, setOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const isMobile = useMediaQuery("(max-width: 768px)");

  const theme = createTheme({
    palette: {
      mode: darkMode ? "dark" : "light",
      primary: {
        main: darkMode ? "#90caf9" : "#1976d2",
      },
      background: {
        default: darkMode ? "#121212" : "#f4f6fb",
        paper: darkMode ? "#1a1a1c" : "#ffffff",
      },
    },
    shape: { borderRadius: 16 },
    typography: { fontFamily: 'Roboto, sans-serif' },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      {/* NAVBAR (desktop only) */}
      {!isMobile && (
        <AppBar
          position="fixed"
          elevation={3}
          sx={{
            backdropFilter: "blur(14px)",
            background: darkMode ? "rgba(18,18,18,0.85)" : "rgba(255,255,255,0.85)",
            borderBottom: darkMode ? "1px solid #333" : "1px solid #e0e0e0",
          }}
        >
          <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="h6" fontWeight={700} color="primary">
              Electrical Distribution Maps
            </Typography>

            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <IconButton
                aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
                onClick={() => setDarkMode(!darkMode)}
                sx={{
                  p: 1.5,
                  borderRadius: 3,
                  background: darkMode ? "#333" : "#f0f0f0",
                  transition: "0.3s ease",
                  fontSize: 20
                }}
              >
                {darkMode ? "🌙" : "☀️"}
              </IconButton>

              <IconButton aria-label="Open menu" onClick={() => setOpen(true)}>
                <MenuIcon />
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>
      )}

      {/* MOBILE BOTTOM NAV */}
      {isMobile && (
        <Box
          sx={{
            position: "fixed",
            bottom: 0,
            left: 0,
            right: 0,
            display: "flex",
            justifyContent: "center",
            py: 1.5,
            background: darkMode ? "#121212" : "#ffffff",
            borderTop: darkMode ? "1px solid #333" : "1px solid #e0e0e0",
          }}
        >
          <IconButton aria-label="Open menu" onClick={() => setOpen(true)}>
            <MenuIcon />
          </IconButton>
        </Box>
      )}

      {/* LEFT DRAWER */}
      <Drawer anchor="left" open={open} onClose={() => setOpen(false)}>
        <Box sx={{ width: 280, p: 3, bgcolor: theme.palette.background.paper }} role="presentation" onClick={() => setOpen(false)}>
          <Typography variant="h6" fontWeight={700} gutterBottom>
            Navigation
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <List>
            {['Dashboard','Profile','Settings','Help'].map((text) => (
              <ListItemButton key={text} sx={{ borderRadius: 2, mb: 1, '&:hover': { backgroundColor: theme.palette.primary.light, color: '#fff' }}}>
                <ListItemText primary={text} />
              </ListItemButton>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* MAIN CONTENT */}
      <Box sx={{ pt: isMobile ? 6 : 14, p: 4, marginTop: 10, display: 'flex', justifyContent: 'center' }}>
        <Box
          sx={{
            background: theme.palette.background.paper,
            p: 5,
            height: "100vh",
            width: '100%',
            maxWidth: 1200,
            minHeight: '500px',
            borderRadius: 6,
            boxShadow: darkMode
              ? "0 10px 40px rgba(0,0,0,0.6)"
              : "0 10px 40px rgba(16,24,40,0.08)",
            transition: "all 0.3s ease",
          }}
        >
          <Mainmap/>
        </Box>
      </Box>
    </ThemeProvider>
  );
}


export default  HomePage