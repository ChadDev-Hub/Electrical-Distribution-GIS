import React,{useEffect, useState} from "react";
import useWebSocket from "react-use-websocket";
import{WSContext} from "./webSocketContext"

export function WebSocketProvider({children}){
    const [dasBoardData, setDashBoardData] = useState({
        inactiveConsumer:[],
        totalConsumer:[],
        plLength:[]
    })

    const [mapData, setMapData] = useState({
            substationData: [],
            primaryLineData: [],
            dtData: [],
            slData: [],
            consumerData: [],
    
        })

    const {lastJsonMessage:mapMsg}= useWebSocket("http://127.0.0.1:8000/ws/mapdata");
    const {lastJsonMessage:dashBoardMsg} = useWebSocket("http://127.0.0.1:8000/ws/dashboard");
    // USE EFFECT FOR MAP DATA
    useEffect(() => {
        const getMapData = async() =>{
            setMapData({
                substationData: mapMsg.features[0].substation,
                primaryLineData: mapMsg.features[1].primary_lines,
                dtData: mapMsg.features[2].distribtion_transformer,
                slData: mapMsg.features[3].secondary_line,
                consumerData: mapMsg.features[4].consumer
            })
        }
        if (!mapMsg) return; // early return inside effect, not before
        switch (mapMsg.type) {
            case "FeatureCollection":
                getMapData();
                break;
            default:
                break;
        }
 
    }, [mapMsg]);

    // USE EFFECT FOR CONSUMER DATA
    useEffect(()=>{
        const dashBoadData = async()=>{
            setDashBoardData({
                inactiveConsumer: dashBoardMsg.inactive_consumer,
                totalConsumer: dashBoardMsg.total_consumer,
                plLength: dashBoardMsg.primary_line_length
            }) 
        }
        if (!dashBoardMsg) {
            return
        }
        switch (dashBoardMsg.type) {
            case "dashboard":
                dashBoadData()
                break;
            default:
                break;
        }
    },[dashBoardMsg])

    const values ={
        map: mapData,
        dashboard: dasBoardData
    }

    return (
        <WSContext.Provider value={values}>
            {children}
        </WSContext.Provider>
    );
};

