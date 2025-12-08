import React, {useState, useEffect} from "react";
import { Marker, Popup } from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import SubstationImage from "../../../assets/station.png"
import { SubstationIcon, InactiveSubstationIcon } from "./icons";
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import CardActions from '@mui/material/CardActions';
import Tooltip from '@mui/material/Tooltip';
import { Container, Stack, Switch } from "@mui/material";
import { renderToStaticMarkup } from "react-dom/server";
import CircularProgress from '@mui/material/CircularProgress';
import axios from "axios";
function SubstationMarker(props){
    const [loadingSwitch, setLoadingSwitch] = useState({});
      // ICONS 
    const substationIcon = new L.Icon({
        iconUrl: SubstationImage,
        iconSize: [15,15]
    })
    const InactiveSubstation = L.divIcon({
        html: renderToStaticMarkup(<InactiveSubstationIcon color="primary" />)
    });



// SWITCH FOR SUBSTATION
    const handleSwitch = async (event, substationId) => {
        setLoadingSwitch(prev => ({ ...prev, [substationId]: true }))
        try {
            const formData = new FormData()
            formData.append("substation_name", substationId)
            formData.append("substation_status", event.target.checked)
            await axios.post("http://127.0.0.1:8000/update/substation", formData, {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            })

        }
        finally {
            setLoadingSwitch(prev => ({ ...prev, [substationId]: false }))
        }

    }
    return(
        <Marker 
        
                icon={props.isactive ? substationIcon : InactiveSubstation} 
                 position={
                    [props.coordinates[1], props.coordinates[0]]}>
                    <Popup autoClose={false} closeOnClick={false}>
                        <Card sx={{ width: "100%" }}>

                            <CardActionArea href={props.image} sx={{ width: "100%" }}>
                                <CardMedia
                                    height="140"
                                    component="img"
                                    image={props.image ? props.image : undefined}
                                />
                                <CardContent >
                                    <Typography gutterBottom variant="h6" component="div">
                                        <strong>{props.substationName}</strong>
                                    </Typography>
                                    <Typography variant="body6" sx={{ color: 'text.secondary' }}>
                                        <strong>{props.description}</strong>
                                        <p><strong>Voltage Rating: </strong>{props.voltageRating}</p>
                                        <p><strong>status: </strong>{props.isactive ? "Active" : "Inactive"}</p>
                                    </Typography>
                                </CardContent>
                            </CardActionArea>
                        
                        <CardActions>
                            <Stack sx={{ justifyContent: 'flex-end', width: "100%", bgcolor: "ivory" }} direction="row">
                                {
                                    loadingSwitch[props.substationName] ? (<CircularProgress size="25px" />) :
                                        (<Tooltip title={`Turn ${props.isactive ? "Off" : "On"} Substation`}>
                                            <Switch name="switch" size="small" checked={props.isactive} onChange={(event) => handleSwitch(event, props.substationName)} />
                                        </Tooltip>)
                                }
                            </Stack>
                        </CardActions>
                        </Card>
                    </Popup>
                </Marker>
    )
}

export default SubstationMarker;