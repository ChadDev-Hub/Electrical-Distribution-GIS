import React, { useEffect, useState } from "react";
import { Grid, Typography, Paper, Box, Fab, Container, Stack, Collapse, Grow } from "@mui/material";
import ExploreRoundedIcon from '@mui/icons-material/ExploreRounded';
import electricalBackground from './assets/Electric-Pole.jpg'
import ReadMoreRoundedIcon from '@mui/icons-material/ReadMoreRounded';


function LandingPage(props) {
    const [readMore, setReadMore] = useState(false)
    const readMe = [
        {
            title: "THE GIS SYSTEMS INCLUDES",
            content: "Interactive Explicit GIS Based Distribution System Includes",
            list: ["Substations", "Primary distribution lines", "Distribution transformers", "Secondary lines", "Customer locations"],
            transition: 500
        },
        {
            title: "Real-Time Network Interaction",
            content: "The platform allows users to interactively control and analyze the network.Substations and transformers can be turned on or off, instantly reflecting their impact on the system.",
            list: ["Identifies disconnected or inactive consumers", "Highlights affected service areas", "Displays the downstream impact on the distribution network"],
            transition: 1000
        }
    ]


    return (
        <Box overflow="scroll" onScroll={()=>setReadMore(!readMore)} sx={{
            backgroundImage: `url(${electricalBackground})`,
            backgroundSize: "cover",
            height: "100vh",
            
        }}
        >
            <Stack direction="row" justifyContent="center" sx={{ p: props.isMobile ? 0 : 4 }}>
                <Box textOverflow="inherit" sx={{
                    m: props.isMobile ? 1 : 3,
                    p: props.isMobile ? 2 : 3,
                    maxWidth: 1000,
                    width: "100%",
                    backgroundColor: "rgba(255, 255, 255, 0.2)",
                    backdropFilter: "blur(0.2rem)",
                    height: "100%",
                    borderRadius: 1
                }}>
                    <Typography textAlign={props.isMobile ? "center" : "left"} variant={props.isMobile ? "h5" : "h3"} sx={{ color: "black", fontWeight: "bold", fontFamily: "ui-sans-serif" }}>
                        ELECTRICAL DISTRIBUTION SYSTEM MAP
                    </Typography>
                    <Typography color="black" variant="h6" m={2}>
                        This GIS-based Electrical Distribution System provides a complete,
                        interactive map of the utility’s entire franchise area.
                        It visualizes the full power distribution network from substations down to individual customers in a single,
                        intuitive and scaleable GIS Application.
                    </Typography>
                    <Stack gap={2} sx={{ width: "100%" }} direction="row" justifyContent="flex-end">
                        <Fab variant="extended" onClick={() => setReadMore(!readMore)}>
                            Read
                            <ReadMoreRoundedIcon />
                        </Fab>
                        <Fab
                            variant="extended"
                            href="/homepage/map">
                            Explore
                            <ExploreRoundedIcon />
                        </Fab>

                    </Stack>
                </Box>
            </Stack>
            <Stack justifyContent="space-evenly" gap={2} alignContent="space-evenly" direction={props.isMobile ? "column" : "row"} px={props.isMobile ? 1 : 10}>
                {readMe.map((r, index) => (
                    <Grow timeout={r.transition} in={readMore}>
                        <Box

                            sx={{
                                width: props.isMobile ? "100%" : "40%",
                                backgroundColor: "rgba(255, 255, 255, 0.2)",
                                backdropFilter: "blur(0.2rem)",
                                height: "80%",
                                borderRadius: 1,
                                p: 3
                            }}>
                            <Typography

                                fontFamily="ui-sans-serif"
                                textAlign="center"
                                color="black"
                                variant={props.isMobile ? "h5" : 'h4'}>
                                {r.title}
                            </Typography>
                            <Typography color="black" variant="h6">
                                {r.content}
                            </Typography>
                            <Typography color="black">
                                <ul>
                                    {r.list.map((l) => <li>{l}</li>)}
                                </ul>
                            </Typography>


                        </Box>

                    </Grow>))}

            </Stack>
        </Box>
    )
}
export default LandingPage;