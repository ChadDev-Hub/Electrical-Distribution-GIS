import React from "react";
import { Marker, Popup } from "react-leaflet";
import ElectricMeterIcon from '@mui/icons-material/ElectricMeter';
import { renderToStaticMarkup, renderToString } from "react-dom/server";
import L from "leaflet"
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
function ConsumerMarker(props){
    const ElectricMeter = L.divIcon({
        html: renderToString(<ElectricMeterIcon style={{color: props.status ? "green": "grey"}} />),
        className:""
    })
    return (
        <Marker position={[props.coordinates[1], props.coordinates[0]]} icon={ElectricMeter}>
            <Popup>
                <Card>
                    <CardContent>
                        <Typography gutterBottom variant="h5" component="div">
                            Consumer Meter
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                            <strong>ACCOUNT NO: </strong> {props.accountNumber} <br />
                            <strong>NAME: </strong> {props.name} <br />
                            <strong>TYPE: </strong> {props.type} <br />
                            <strong>BRAND: </strong> {props.brand} <br />
                            <strong>SERIAL NUMBER: </strong> {props.SerialNumber} <br />
                            <strong>VILLAGE: </strong> {props.village} <br />
                            <strong>MUNICIPALITY: </strong> {props.municipality} <br />
                            <strong>STATUS: </strong> {props.status? "Active": "Inactive"} <br />
                        </Typography>
                    </CardContent>
                </Card>

            </Popup>
        </Marker>
    )
}

export default ConsumerMarker;