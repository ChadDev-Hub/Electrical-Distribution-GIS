import React from "react";
import { Polyline } from "react-leaflet";



function SecondaryLine(props){
    return(
        <Polyline pathOptions={{color: props.isactive? "blue" : "grey", dashArray: "10, 6", weight:1}} positions={[
            [props.coordinates[0][1], props.coordinates[0][0]],
            [props.coordinates[1][1], props.coordinates[1][0]]
        ]}>
        </Polyline>
    )
}
export default SecondaryLine;