import React, { useEffect, useState } from "react";
import { Marker, useMap} from "react-leaflet";
import BoyRoundedIcon from '@mui/icons-material/BoyRounded';
import L from 'leaflet'
import {renderToString } from "react-dom/server";

function RealTimeMarker(props){
    const map = useMap()
    const [position, setPosition] = useState()
    const realTimeIcon = L.divIcon({
        html: renderToString(<BoyRoundedIcon style={{ fontSize: 30, color: "#1976d2" }}/>),
        className:"",
        iconAnchor: [20, 40],
        
    })
    useEffect(()=>{
        if (props.realtimepos){
            map.flyTo(props.realtimepos)
        }
    },[props.realtimepos])
    
    useEffect(()=>{
            const interval = setInterval(()=>{
                navigator.geolocation.getCurrentPosition((pos)=>{
                    setPosition([pos.coords.latitude,pos.coords.longitude]);
                });
            },2000)
            return () => clearInterval(interval)
        },[]);
    if (!position) return null;
    return(
        <Marker position={position} icon={realTimeIcon}>
               
        </Marker>
    );
}

export default RealTimeMarker