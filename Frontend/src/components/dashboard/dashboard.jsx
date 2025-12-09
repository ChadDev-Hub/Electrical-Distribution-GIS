import React, { useEffect, useState } from "react";
import useWebSocket from "react-use-websocket";
import InactiveTable from "./components/table";
import { Box } from "@mui/material";
function DashBoard(){
    const [inactiveConsumer, setInactiveConsumer] = useState([])

    const socketUrl = "http://127.0.0.1:8000/ws/dashboard"
    const {lastJsonMessage} = useWebSocket( socketUrl )
    useEffect(()=>{
        const getInactiveConsumer = async() =>{
            setInactiveConsumer(lastJsonMessage)}
        if(!lastJsonMessage){
            return
        }
        
        switch (lastJsonMessage.type) {
            case "dashboard":
                getInactiveConsumer()
                break;
            default:
                break;
        }},[lastJsonMessage])
    return (
        <Box sx={{display:"flex",justifyContent:"center", marginTop:10}}>
            {inactiveConsumer && <InactiveTable inactiveConsumer={inactiveConsumer.inactive_consumer}/>}
        </Box>
            

    )
}
export default DashBoard;