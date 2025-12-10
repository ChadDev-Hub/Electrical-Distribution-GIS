import React from "react";
import InactiveTable from "./components/table";
import { Box } from "@mui/material";
import { useWS } from "../webSocketContext";
function DashBoard() {
    const { dashboard } = useWS()
    console.log(dashboard.inactiveConsumer)
    return (
        <Box sx={{ display: "flex", justifyContent: "center", marginTop: 10 }}>
            <InactiveTable inactiveConsumer={dashboard.inactiveConsumer}/>
        </Box>
    )
}
export default DashBoard;