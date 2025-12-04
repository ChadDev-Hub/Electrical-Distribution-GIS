import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, Tooltip as LeafletToolTip } from 'react-leaflet'
import Button from '@mui/material/Button';
import ElectricBoltIcon from '@mui/icons-material/ElectricBolt';
import useWebSocket from "react-use-websocket";
import { SubstationIcon, InactiveSubstationIcon } from "./components/icons";
import { renderToStaticMarkup } from "react-dom/server";
import { Container, Stack, Switch } from "@mui/material";
import CircularProgress from '@mui/material/CircularProgress';
import axios from "axios";
import L from 'leaflet';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import CardActions from '@mui/material/CardActions';
import Tooltip from '@mui/material/Tooltip';
import SubstationImage from "../../assets/station.png"
import TransformerGroup from "./components/transformergroup";
import RealtimeButton from "./components/realtimelocationButton";
import RealTimeMarker from "./components/realtimeMarker";
function Mainmap() {
    const [substationData, setSubstationData] = useState([]);
    const [primaryLineData, setPrimaryLineData] = useState([]);
    const [dtData, setdtData] = useState([])
    const [loadingSwitch, setLoadingSwitch] = useState({});
    const [showRealTimeLoc, setRealTimeLoc] = useState(false)

    // CENTER MAP POSITION
    const position = [12.102462, 120.031814];

    // SOCKET URL
    const socketUrl = "http://127.0.0.1:8000/ws/mapdata";

    // ICONS 
    const substationIcon = new L.Icon({
        iconUrl: SubstationImage,
        iconSize: [15,15]
    })
    const InactiveSubstation = L.divIcon({
        html: renderToStaticMarkup(<InactiveSubstationIcon color="primary" />)
    });
    const { lastJsonMessage } = useWebSocket(
        socketUrl,
        {
            shouldReconnect: true
        }
    );

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
    // SET LATESTS MAPS DATA SENDS BY WEBSOCKET
    useEffect(() => {
        const update_mapdata = async () => {
            setSubstationData(lastJsonMessage.features[0].substation)
            setPrimaryLineData(lastJsonMessage.features[1].primary_lines)
            setdtData(lastJsonMessage.features[2].distribtion_transformer)
        }
        if (lastJsonMessage) {
            update_mapdata()
        }
    }, [lastJsonMessage])

    // TOGGLE REALTIME POSITION
    const showRealtime =() => {
        setRealTimeLoc(!showRealTimeLoc)
    }

    return (
        <Container maxWidth={false}  sx={{position:"relative", width:"100vw", height:"100vh", p:0}}>
            <RealtimeButton showRealtime={showRealtime} showRealTimeLoc={showRealTimeLoc}/>
            <MapContainer center={position} zoom={9} scrollWheelZoom={true} style={{ height: "100%", width: "100%" }}>
            <TileLayer
                attribution='&copy; <a href="https://carto.com/attributions">CARTO / OpenStreetMap</a>'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                
            />
            {substationData && substationData.map((m) => (

                <Marker 
                icon={m.properties.isactive ? substationIcon : InactiveSubstation} 
                key={m.properties.substation_name} position={
                    [m.geometry.coordinates[1], m.geometry.coordinates[0]]}>
                    <Popup autoClose={false} closeOnClick={false}>
                        <Card sx={{ width: "100%" }}>

                            <CardActionArea href={m.properties.image} sx={{ width: "100%" }}>
                                <CardMedia
                                    height="140"
                                    component="img"
                                    image={m.properties.image}
                                />
                                <CardContent >
                                    <Typography gutterBottom variant="h6" component="div">
                                        <strong>{m.properties.substation_name}</strong>
                                    </Typography>
                                    <Typography variant="body6" sx={{ color: 'text.secondary' }}>
                                        <strong>{m.properties.description}</strong>
                                        <p><strong>Voltage Rating: </strong>{m.properties.voltage_rating}</p>
                                        <p><strong>status: </strong>{m.properties.isactive ? "Active" : "Inactive"}</p>
                                    </Typography>
                                </CardContent>
                            </CardActionArea>
                        
                        <CardActions>
                            <Stack sx={{ justifyContent: 'flex-end', width: "100%", bgcolor: "ivory" }} direction="row">
                                {
                                    loadingSwitch[m.properties.substation_name] ? (<CircularProgress size="30px" />) :
                                        (<Tooltip title={`Turn ${m.properties.isactive ? "Off" : "On"} Substation`}>
                                            <Switch name="switch" size="small" checked={m.properties.isactive} onChange={(event) => handleSwitch(event, m.properties.substation_name)} />
                                        </Tooltip>)
                                }
                            </Stack>
                        </CardActions>
                        </Card>
                    </Popup>
                </Marker>
            ))}
            {primaryLineData && primaryLineData.map((pl) => (
                <Polyline
                    key={pl.id}
                    eventHandlers={{ mouseover: () => console.log("Primary Lines") }} pathOptions={{ color: pl.properties.isactive ? "orange" : "grey"}} positions={
                        [[pl.geometry.coordinates[0][1], pl.geometry.coordinates[0][0]],
                        [pl.geometry.coordinates[1][1], pl.geometry.coordinates[1][0]]]}>
                    <LeafletToolTip>
                        Primary Line
                    </LeafletToolTip>
                    <Popup>
                        <p><strong>Line Id: </strong>{pl.properties.primary_line_id}</p>
                        <p><strong>From Node: </strong>{pl.properties.from_node}</p>
                    </Popup>
                </Polyline>
            ))}
            {dtData && <TransformerGroup transformerData = {dtData}/>}
            {showRealTimeLoc && <RealTimeMarker/>}
        </MapContainer>
        </Container>
        
        
        

    )
}

export default Mainmap;