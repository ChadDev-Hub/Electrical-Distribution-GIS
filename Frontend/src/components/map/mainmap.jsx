import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, LayerGroup, LayersControl, Tooltip as LeafletToolTip } from 'react-leaflet'
import Button from '@mui/material/Button';
import ElectricBoltIcon from '@mui/icons-material/ElectricBolt';
import useWebSocket from "react-use-websocket";
import SubstationMarker from "./components/substation";
import { renderToStaticMarkup } from "react-dom/server";
import { Container, Stack, Switch } from "@mui/material";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from 'leaflet';
import TransformerGroup from "./components/transformergroup";
import RealtimeButton from "./components/realtimelocationButton";
import RealTimeMarker from "./components/realtimeMarker";
import SecondaryLine from "./components/secondaryLine";

function Mainmap() {
    const [substationData, setSubstationData] = useState([]);
    const [primaryLineData, setPrimaryLineData] = useState([]);
    const [dtData, setdtData] = useState([]);
    const [slData, setSlData] = useState([]);
    const [showRealTimeLoc, setRealTimeLoc] = useState(false);

    // CENTER MAP POSITION
    const position = [12.102462, 120.031814];

    // SOCKET URL
    const socketUrl = "http://127.0.0.1:8000/ws/mapdata";


    const { lastJsonMessage } = useWebSocket(
        socketUrl
    );


    // SET LATESTS MAPS DATA SENDS BY WEBSOCKET
    useEffect(() => {
        const update_mapdata = async () => {
            setSubstationData(lastJsonMessage.features[0].substation)
            setPrimaryLineData(lastJsonMessage.features[1].primary_lines)
            setdtData(lastJsonMessage.features[2].distribtion_transformer)
            setSlData(lastJsonMessage.features[3].secondary_line)
        }
        if (!lastJsonMessage) return;

        switch (lastJsonMessage.type) {
            case "FeatureCollection":
                update_mapdata()
                break;

        }
    }, [lastJsonMessage])

    // TOGGLE REALTIME POSITION
    const showRealtime = () => {
        setRealTimeLoc(!showRealTimeLoc)
    }
    console.log(slData)
    return (
        <Container maxWidth={false} sx={{ position: "relative", width: "100vw", height: "100vh", p: 0 }}>
            <RealtimeButton showRealtime={showRealtime} showRealTimeLoc={showRealTimeLoc} />
            <MapContainer center={position} zoom={9} scrollWheelZoom={true} style={{ height: "100%", width: "100%" }}>
                <TileLayer
                    attribution='&copy; <a href="https://carto.com/attributions">CARTO / OpenStreetMap</a>'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

                />
                <LayersControl position="topleft">     
                    <LayersControl.Overlay name="Substation" checked>
                        <LayerGroup>
                            {/* SUBSTATION DATA */}
                            {substationData && substationData.map((m) => (
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
                            {primaryLineData && primaryLineData.map((pl) => (
                                <Polyline
                                    key={pl.id}
                                    eventHandlers={{ mouseover: () => console.log("Primary Lines") }} 
                                    pathOptions={{ color: pl.properties.isactive ? "orange" : "grey",
                                        weight:2 }} positions={
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
                            {dtData &&
                                <MarkerClusterGroup
                                    spiderfyOnMaxZoom={true}

                                >
                                    {dtData.map((dt) => (
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
                    <LayersControl.Overlay name="Secondary Line">
                        <LayerGroup>
                            {slData && slData.map((sl)=>(
                                <SecondaryLine
                                key={sl.id}
                                coordinates={sl.geometry.coordinates}
                                isactive = {sl.properties.isactive}
                                />
                            ))}
                        </LayerGroup>

                    </LayersControl.Overlay>

                </LayersControl>

                {showRealTimeLoc && <RealTimeMarker />}
            </MapContainer>
        </Container>
    )
}

export default Mainmap;