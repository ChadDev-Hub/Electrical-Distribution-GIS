import React, { useRef, useState } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, LayerGroup, LayersControl, Tooltip as LeafletToolTip, useMapEvent } from 'react-leaflet'
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
import Loader from "../../loader"
import SearchConsumer from "./components/searchConsumer";
import LayerToggle from "./components/layertogglelistener";
import Collapse from '@mui/material/Collapse';
function Mainmap(props) {
    const [showRealTimeLoc, setRealTimeLoc] = useState(false);
    const [realtimePosition, setRealTimePosition] = useState(null)
    const markerRefs = useRef({})
    const clusterGroupRef = useRef()
    const [showSearch, setShowSearch] = useState(false)

    // CENTER MAP POSITION;
    const position = [12.102462, 120.031814];

    const { map, mapLoading } = useWS();
    const mapData = map;

    // TOGGLE REALTIME POSITION
    const showRealtime = () => {
        setRealTimeLoc(!showRealTimeLoc);
        navigator.geolocation.getCurrentPosition((pos) => {
            setRealTimePosition([pos.coords.latitude, pos.coords.longitude])
        });
    }

    const consumerData = map?.consumerData.map((d) => ({
        id: d.id,
        label: `${d.properties.account_no} | ${d.properties.name}`,
        location: [d.geometry.coordinates[1], d.geometry.coordinates[0]]
    }))

    return (
        <Grid container sx={{ height: "100vh", weight: "100vh", }}>
            <Grid size={12} sx={{ p: props.isMobile ? 2 : 10, paddingBottom: props.isMobile ? 12 : 3 }}>
                <MapContainer center={position} zoom={9} scrollWheelZoom={true} style={{ height: "100%", width: "100%", borderRadius: 20 }}>
                    
                    {mapLoading && <Box
                        sx={{
                            height: "100%",
                            position: "relative",
                            inset: 0,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            backgroundColor: "rgba(225, 223, 223, 0.28)", // optional dim
                            zIndex: 1000
                        }}>
                        <Loader />

                    </Box>}
                    {/* SEARCH BAR */}
                    {consumerData &&
                        <Collapse orientation="horizontal" in={showSearch}>
                                    <SearchConsumer options={consumerData} markerRefs={markerRefs} clusterGroupRef={clusterGroupRef} isMobile={props.isMobile}/>
                        </Collapse>
                    }
                    <RealtimeButton isMobile={props.isMobile} showRealtime={showRealtime} showRealTimeLoc={showRealTimeLoc} />
                    <TileLayer
                        attribution='&copy; <a href="https://carto.com/attributions">CARTO / OpenStreetMap</a>'
                        url={props.darkMode ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}
                    />
                    <LayerToggle setShowSearch={setShowSearch} />
                    <LayersControl position={props.isMobile?"topright" :"topleft"}>
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
                                                dttype={dt.properties.type}
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
                                    ref={clusterGroupRef}
                                    disableClusteringAtZoom={18}
                                    showCoverageOnHover={false}
                                    chunkedLoading={true}
                                >
                                    {mapData.consumerData.map((c) => (
                                        <ConsumerMarker
                                            key={c.id}
                                            id={c.id}
                                            coordinates={c.geometry.coordinates}
                                            accountNumber={c.properties.account_no}
                                            name={c.properties.name}
                                            type={c.properties.type}
                                            brand={c.properties.brand}
                                            serialNumber={c.properties.serial_number}
                                            village={c.properties.village}
                                            municipality={c.properties.municipality}
                                            status={c.properties.status}
                                            markerRefs={markerRefs}
                                        />
                                    ))}
                                </MarkerClusterGroup>}
                            </LayerGroup>
                        </LayersControl.Overlay>


                    </LayersControl>
                    {showRealTimeLoc && <RealTimeMarker realtimepos={realtimePosition} />}
                </MapContainer>

            </Grid>

        </Grid>
    )
}

export default Mainmap;