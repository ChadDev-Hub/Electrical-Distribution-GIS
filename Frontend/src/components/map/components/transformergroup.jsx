import React from "react";
import MarkerClusterGroup from "react-leaflet-cluster";
import { Marker, Popup } from "react-leaflet";
import { Card, CardActionArea, CardMedia, CardContent, } from "@mui/material";
import {Typography} from "@mui/material";
import transformerIcon from "../../../assets/transformer.png"
import L from 'leaflet';
function TransformerGroup(props){
    const dtIcon = new L.Icon(
        {
            iconUrl: transformerIcon,
            iconSize: [15,15]

        }
    )

    return(
        <MarkerClusterGroup>
            {props.transformerData && props.transformerData.map((dt)=>(
                <Marker
                key={dt.id}
                position={[dt.geometry.coordinates[1], dt.geometry.coordinates[0]]}
                icon={dtIcon}>
                    <Popup>
                        <Card>
    
                                <CardActionArea href={dt.properties.image} target="_blank" sx={{width: "100%"}}>
                                <CardMedia
                                loading={dt.properties.image? false: true}
                                width="100%"
                                height="200"
                                component="img"
                                image={dt.properties.image}
                                />
                                </CardActionArea>
                        
                            <CardActionArea sx={{width: "100%"}}>
                            <CardContent>
                                <Typography gutterBottom variant="h6" component="div">
                                    <strong>{dt.properties.transformer_id}</strong>
                                </Typography>
                                <Typography variant="body6" fontSize={12} component="div" sx={{width:"100%"}}>
                                    <strong>{dt.properties.type}</strong>
                                    <p><strong>Description: </strong>{dt.properties.description}</p>
                                    <p><strong>Village: </strong>{dt.properties.village}</p>
                                    <p><strong>Municipality: </strong>{dt.properties.municipality}</p>
                                    <p><strong>Status: </strong>{dt.properties.isactive}</p>
                                </Typography>
                            </CardContent>
                            </CardActionArea>
                        </Card>
                    </Popup>
                </Marker>
            ))}
        </MarkerClusterGroup>
    )
}

export default TransformerGroup;