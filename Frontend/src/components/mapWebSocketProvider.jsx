import React,{useEffect, useState} from "react";
import useWebSocket from "react-use-websocket";
import{WSContext} from "./webSocketContext"


export function WebSocketProvider({children}){
     const baseUrl = import.meta.env.VITE_BASE_URL
    const [dasBoardData, setDashBoardData] = useState({
        inactiveConsumer:[],
        totalConsumer:[],
        plLength:[],
        slLength:[]
    })
    
    const [mapLoading, setMapLoading] = useState(true)
    const [mapData, setMapData] = useState({
            substationData: [],
            primaryLineData: [],
            dtData: [],
            slData: [],
            consumerData: [],
    
        })

    const {lastJsonMessage:mapMsg} = new useWebSocket(`${baseUrl}/ws/mapdata`,
        {
            shouldReconnect: () => true,
        }
    );

    const {lastJsonMessage:dashBoardMsg} = new  useWebSocket(`${baseUrl}/ws/dashboard`,
        {
            shouldReconnect: () => true,
        }
    );
    

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
            setMapLoading(false);
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
                plLength: dashBoardMsg.primary_line_length,
                slLength: dashBoardMsg.secondary_line_length
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
        dashboard: dasBoardData,
        mapLoading: mapLoading
    }

    return (
        <WSContext.Provider value={values}>
            {children}
        </WSContext.Provider>
    );
};

