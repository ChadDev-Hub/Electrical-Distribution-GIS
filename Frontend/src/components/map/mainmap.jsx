import React, { useState } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, LayerGroup, LayersControl, Tooltip as LeafletToolTip, ZoomControl } from 'react-leaflet'
import Button from '@mui/material/Button';
import ElectricBoltIcon from '@mui/icons-material/ElectricBolt';
import SubstationMarker from "./components/substation";
import { Container, Stack, Switch, Zoom, Box, Grid } from "@mui/material";
import MarkerClusterGroup from 'react-leaflet-cluster';
import L from 'leaflet';
import TransformerGroup from "./components/transformergroup";
import RealtimeButton from "./components/realtimelocationButton";
import RealTimeMarker from "./components/realtimeMarker";
import SecondaryLine from "./components/secondaryLine";
import ConsumerMarker from "./components/consumer";
import { useWS } from "../webSocketContext";
function Mainmap(props) {
    
    const [showRealTimeLoc, setRealTimeLoc] = useState(false);

    // CENTER MAP POSITION
    const position = [12.102462, 120.031814];

 
    const {map} = useWS();
    const mapData = map; // safe optional chaining

    

    // TOGGLE REALTIME POSITION
    const showRealtime = () => {
        setRealTimeLoc(!showRealTimeLoc)
    }
    console.log(mapData)
    return (
        
        <Grid container sx={{height:"100vh", weight:"100vh"}}>
            <Grid size={12} sx={{p:props.isMobile? 2: 10, paddingBottom:props.isMobile? 12: 3}}>
                <MapContainer center={position} zoom={9} scrollWheelZoom={true} style={{height: "100%", width: "100%" , borderRadius: 20 }}>
                <RealtimeButton showRealtime={showRealtime} showRealTimeLoc={showRealTimeLoc} />
                <TileLayer
                    attribution='&copy; <a href="https://carto.com/attributions">CARTO / OpenStreetMap</a>'
                    url={props.darkMode? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}
                />
                <LayersControl position="topleft">
                    <LayersControl.Overlay name="Substation" checked>
                        <LayerGroup>
                            {/* SUBSTATION DATA */}
                            {mapData.substationData && mapData.substationData.map((m) => (
                                <SubstationMarker
                                    key={m.id}
                                    isactive={m.properties.isactive}
                                    substationName={m.properties.substation_name}
                                    coordinates={m.geometry.coordinates}
                                    image={m.properties.image}
                                    description={m.properties.description}
                                    voltageRating={m.properties.voltage_rating}
                                />
                            ))}

                        </LayerGroup>

                    </LayersControl.Overlay>
                    <LayersControl.Overlay name="Primary Line" checked>
                        <LayerGroup>
                            {/* PRIMARY LINE DATA */}
                            {mapData.primaryLineData && mapData.primaryLineData.map((pl) => (
                                <Polyline
                                    key={pl.id}
                                    eventHandlers={{ mouseover: () => console.log("Primary Lines") }}
                                    pathOptions={{
                                        color: pl.properties.isactive ? "orange" : "grey",
                                        weight: 2
                                    }} positions={
                                        [[pl.geometry.coordinates[0][1], pl.geometry.coordinates[0][0]],
                                        [pl.geometry.coordinates[1][1], pl.geometry.coordinates[1][0]]]}
                                >
                                    <LeafletToolTip>
                                        Primary Line
                                    </LeafletToolTip>
                                    <Popup>
                                        <p><strong>Line Id: </strong>{pl.properties.primary_line_id}</p>
                                        <p><strong>From Node: </strong>{pl.properties.from_node}</p>
                                    </Popup>
                                </Polyline>
                            ))}
                        </LayerGroup>


                    </LayersControl.Overlay>
                    <LayersControl.Overlay name="Transformer" checked>
                        <LayerGroup>
                            {/* CLUSTER GROUP FOR TRANSFORMER DATA */}
                            {mapData.dtData &&
                                <MarkerClusterGroup
                                    spiderfyOnMaxZoom={true}

                                >
                                    {mapData.dtData.map((dt) => (
                                        <TransformerGroup
                                            key={dt.id}
                                            coordinates={dt.geometry.coordinates}
                                            image={dt.properties.image}
                                            transformerId={dt.properties.transformer_id}
                                            description={dt.properties.description}
                                            village={dt.properties.village}
                                            municipality={dt.properties.municipality}
                                            isactive={dt.properties.isactive}
                                        />

                                    )

                                    )}
                                </MarkerClusterGroup>
                            }
                        </LayerGroup>
                    </LayersControl.Overlay>
                    <LayersControl.Overlay name="Secondary Line" checked>
                        {/* SECONDARY LINE */}
                        <LayerGroup>
                            {mapData.slData && mapData.slData.map((sl) => (
                                <SecondaryLine
                                    key={sl.id}
                                    coordinates={sl.geometry.coordinates}
                                    isactive={sl.properties.isactive}
                                />
                            ))}
                        </LayerGroup>

                    </LayersControl.Overlay>

                    <LayersControl.Overlay name="Consumer Meter">
                        {/* Consumer */}
                        <LayerGroup>
                            {mapData.consumerData && <MarkerClusterGroup
                                disableClusteringAtZoom={18}  // number
                                showCoverageOnHover={false}   // optional
                                chunkedLoading={true}

                            >
                                {mapData.consumerData.map((c) => (
                                    <ConsumerMarker
                                        key={c.id}
                                        coordinates={c.geometry.coordinates}
                                        accountNumber={c.properties.account_no}
                                        name={c.properties.name}
                                        type={c.properties.type}
                                        brand={c.properties.brand}
                                        serialNumber={c.properties.serial_number}
                                        village={c.properties.village}
                                        municipality={c.properties.municipality}
                                        status={c.properties.status}
                                    />
                                ))}
                            </MarkerClusterGroup>}
                        </LayerGroup>
                    </LayersControl.Overlay>


                </LayersControl>

                {showRealTimeLoc && <RealTimeMarker />}
            </MapContainer>

            </Grid>
             
        </Grid>
    )
}

export default Mainmap;