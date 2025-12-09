import React, { useState } from "react";
import MarkerClusterGroup from "react-leaflet-cluster";
import { Marker, Popup } from "react-leaflet";
import { Card, CardActionArea, CardMedia, CardContent, Stack, Switch, CircularProgress } from "@mui/material";
import {Typography} from "@mui/material";
import transformerIcon from "../../../assets/transformer.png"
import L from 'leaflet';
import axios from "axios";

function TransformerGroup(props){
    const [loadingSwitch, setLoadingSwitch] = useState({})
    const dtIcon = new L.Icon(
        {
            iconUrl: transformerIcon,
            iconSize: [15,15]
        }
    )
    const handleTransformerSwitch = async(event, transformer_id) => {
        setLoadingSwitch(prev => ({...prev, [transformer_id] : true}))
        try{
            const formData = new FormData()
            formData.append("transformer_id", transformer_id)
            formData.append("status", event.target.checked)
            await axios.post("http://127.0.0.1:8000/update/distribution_transformer",formData,
                {headers: {
                    "Content-Type": "multipart/form-data"
                }}
            )
        }
        catch (error){
            console.log(error)
        }
        finally{
            setLoadingSwitch(prev => ({...prev, [transformer_id]: false}))
        }
    }
    return(
            <Marker
                position={[props.coordinates[1], props.coordinates[0]]}
                icon={dtIcon}>
                    <Popup autoClose={false} closeOnClick={false}>
                        <Card>
                                <CardActionArea href={props.image} target="_blank" sx={{width: "100%"}}>
                                <CardMedia
                                width="100%"
                                height="200"
                                component="img"
                                image={props.image}
                                alt="Transformer"
                                />
                                </CardActionArea>
                        
                            <CardActionArea sx={{width: "100%"}}>
                            <CardContent>
                                <Typography gutterBottom variant="h6" component="div">
                                    <strong>{props.transformerId}</strong>
                                </Typography>
                                <Typography variant="body2" fontSize={12} component="div" sx={{width:"100%"}}>
                                    <strong>{props.type}</strong>
                                    <p><strong>Description: </strong>{props.description}</p>
                                    <p><strong>Village: </strong>{props.village}</p>
                                    <p><strong>Municipality: </strong>{props.municipality}</p>
                                    <p><strong>Status: </strong>{props.isactive ? "Active" : "Inactive"}</p>
                                </Typography>
                            </CardContent>
                            </CardActionArea>
                                <Stack sx={{justifyContent:"flex-end",width: "100%"}} direction="row">
                                    {loadingSwitch[props.transformerId] ? <CircularProgress size="25px"/> 
                                    : <Switch  size="small" checked={props.isactive} onChange={(event)=>handleTransformerSwitch(event, props.transformerId)}/>}       
                                </Stack>
                        </Card>
                    </Popup>
                </Marker>
    )
}

export default TransformerGroup;