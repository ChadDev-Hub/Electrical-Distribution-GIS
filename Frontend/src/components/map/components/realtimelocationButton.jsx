import React from "react";
import { Marker } from "react-leaflet";
import Fab from '@mui/material/Fab';
import NavigationTwoToneIcon from '@mui/icons-material/NavigationTwoTone';
import NavigationRoundedIcon from '@mui/icons-material/NavigationRounded';

function RealtimeButton(props){
    return(
        <Fab onClick={props.showRealtime} size="small" color={props.showRealTimeLoc? "primary":"default"} sx={{position:"absolute", top:10, left:{xs: "85%", md:"95%"}}}>
                {props.showRealTimeLoc? <NavigationRoundedIcon/> :<NavigationTwoToneIcon/>}
        </Fab>
    )
}
export default RealtimeButton