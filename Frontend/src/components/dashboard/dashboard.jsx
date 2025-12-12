import React from "react";
import InactiveTable from "./components/table";
import { Box } from "@mui/material";
import { useWS } from "../webSocketContext";
import PrimarLineLength from "./components/primaryLineLength";
import Grid from '@mui/material/Grid';
import TotalConsumer from "./components/totalConsumer";
function DashBoard(props) {
    const { dashboard } = useWS()
    return (
        <Box sx={{ marginTop: props.isMobile ? 2 : 10, px: 2 }}>
            <Grid container spacing={2} p={{xs: 0, sm: 0, md: 4}}>
                <Grid container size={{ xs: 12, sm: 12, md: 8 }}>
                    <Grid size={{ xs: 12, sm: 12, md: 12 }}>
                        <TotalConsumer totalConsumer={dashboard.totalConsumer} isMobile={props.isMobile} />
                    </Grid>
                    <Grid size={{ xs: 12, sm: 12, md: 12 }}>
                        <InactiveTable isMobile={props.isMobile} inactiveConsumer={dashboard.inactiveConsumer} />
                    </Grid>
                </Grid>
                <Grid container size={{ xs: 12, sm: 12, md: 4 }}>
                    <Grid size={{ xs: 12, sm: 12, md: 12 }}>
                        <PrimarLineLength isMobile={props.isMobile} plLength={dashboard.plLength} />
                    </Grid>

                </Grid>
            </Grid>
        </Box>
    )
}
export default DashBoard;