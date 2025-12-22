import React from "react";
import { useMapEvents } from "react-leaflet";

function LayerToggle({setShowSearch}){
    useMapEvents({
        overlayadd(e){
            if(e.name === "Consumer Meter"){
                setShowSearch(true)
            }
        },
        overlayremove(e){
            if(e.name === "Consumer Meter"){
                setShowSearch(false)
            }
        }
    })
}
export default LayerToggle