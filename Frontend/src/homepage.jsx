import React, { useState } from "react";
import { useTheme } from "@mui/material/styles";
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Drawer,
  Box,
  Divider,
  List,
  ListItemButton,
  ListItemText,
  Stack
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { Outlet, useNavigate } from "react-router-dom";
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
function HomePage(props) {
  const theme = useTheme();
  const navigate = useNavigate()
  const [open, setOpen] = useState(false);
  const menuButon = [{
    "Button": "Map",
    "ref": "/homepage/map"
  },
  {
    "Button": "DashBoard",
    "ref" : '/homepage/dashboard'
  }]


  const handleMenuButtonClick = (event) =>{
      const name = event.currentTarget.dataset.name
      const menuItem = menuButon.find(m => m.Button == name)
      console.log(menuItem)
      if (menuItem.ref) { 
        navigate(menuItem.ref)
      }
  }
  return (
    <>
      {/* NAVBAR (desktop only) */}
      {!props.isMobile && (
        <AppBar
          position="fixed"
          elevation={3}
          sx={{
            backdropFilter: "blur(14px)",
            background: props.darkMode ? "rgba(18,18,18,0.85)" : "rgba(255,255,255,0.85)",
            borderBottom: props.darkMode ? "1px solid #333" : "1px solid #e0e0e0",
          }}
        >
          <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="h6" fontWeight={700} color="primary">
              Electrical Distribution Maps
            </Typography>

            <Box dis sx={{ display: "flex", alignItems: "center", gap: 2 }}>

              <IconButton aria-label="Open menu" onClick={() => setOpen(!open)}>
                <MenuIcon />
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>
      )}

      {/* MOBILE BOTTOM NAV */}
      {props.isMobile && (
        <Box
          sx={{
            mx: 2,
            marginBottom: 3,
            position: "fixed",
            bottom: 0,
            left: 0,
            right: 0,
            display: "flex",
            justifyContent: "center",
            py: 1.5,
            background: props.darkMode ? "#1212122c" : "#bebebe56",
            borderTop: props.darkMode ? "1px solid #5a5454ff" : "1px solid #585858ff",
            zIndex: 9999,
            borderRadius: 60
          }}
        >
          <IconButton color="primary" aria-label="Open menu" onClick={() => setOpen(!open)}>
            <MenuIcon />
          </IconButton>
        </Box>
      )}

      {/* LEFT DRAWER */}
      <Drawer anchor="left" open={open} onClose={() => setOpen(false)}>
        <Box sx={{ width: 280, p: 3, bgcolor: theme.palette.background.paper }} role="presentation" onClick={() => setOpen(false)}>
          <Stack
            alignItems="center"
            direction="row"
            justifyContent="space-between"
            spacing={4}
          >
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Navigation
            </Typography>
            <IconButton
              
              aria-label={props.darkMode ? "Switch to light mode" : "Switch to dark mode"}
              onClick={props.switchTheme}
              sx={{
                color:props.darkMode? "yellow" : "orange",
                position: "flex",
                justifySelf: "center",
                background: props.darkMode ? "#000000ff" : "#f0f0f0",
                transition: "0.3s ease",
                fontSize: 20,

              }}
            >
              {props.darkMode ? <DarkModeIcon/> : <LightModeIcon/>}
            </IconButton>
          </Stack>
          <Divider sx={{ mb: 2, mt: 2 }} />
          <List>
            {menuButon.map((text, index) => (
              <ListItemButton  key={index} data-name={text.Button} onClick={handleMenuButtonClick} sx={{ borderRadius: 2, mb: 1, '&:hover': { backgroundColor: theme.palette.primary.light, color: '#fff' } }}>
                <ListItemText primary={text.Button} />
              </ListItemButton>
            ))}
          </List>
        </Box>
      </Drawer>
      
      {/* MAIN CONTENT */}
            <Outlet/>
    </>
  );
}


export default HomePage