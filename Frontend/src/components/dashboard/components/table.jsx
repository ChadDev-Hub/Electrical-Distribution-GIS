import React from "react";
import { DataGrid } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import { Typography, Paper } from "@mui/material";
function InactiveTable(props) {
    const columName = [
        {
            "field": "id",
            "headerName": "id",
            "headerAlign":"center",
            "width": 80
        },
        {
            "field": "account_no",
            "headerName": "Account #",
            "headerAlign":"center",
            "width": 150
        },
        {
            "field": "consumer_name",
            "headerName": "Consumer Name",
            "headerAlign":"center",
            "width": 150
        },
        {
            "field": "type",
            "headerName": "Type",
            "headerAlign":"center",
            "width": 150
        },
        {
            "field": "brand",
            "headerName": "Brand",
            "headerAlign":"center",
            "width": 150
        },
        {
            "field": "serial_no",
            "headerName": "Serial Number",
            "headerAlign":"center",
            "width": 150
        },
        {
            "field": "village",
            "headerName": "Village",
            "headerAlign":"center",
            "width": 150

        },
        {
            "field": "municipality",
            "headerName": "Municipality",
            "headerAlign":"center",
            "width": 150
        }
    ]
    return (
        <Paper sx={{ 
            height:props.isMobile?300 :600,
            width:"100%",
            border:"1px solid grey", 
            display:"flex", 
            flexDirection:"column"}}>
            <Typography sx={{p:2, fontWeight:"bold"}}>Inactive Consumer Table</Typography>
            <Box sx={{flex:1, minHeight: 0}}>
                <DataGrid
                sx={{height:"100%"}}
                checkboxSelection
                autoPageSize ={true}
                rows={props.inactiveConsumer ?? []}
                columns={columName}
                loading={props.loading}/>

            </Box>
            
        </Paper>
    )
}
export default InactiveTable;