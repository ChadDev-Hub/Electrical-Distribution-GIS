import React from "react";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { DataGrid } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
function InactiveTable(props) {
    const columName = [
        {
            "field": "id",
            "headerName": "id"
        },
        {
            "field": "account_no",
            "headerName": "Account #",
        },
        {
            "field": "consumer_name",
            "headerName": "Consumer Name"
        },
        {
            "field": "type",
            "headerName": "Type"
        },
        {
            "field": "brand",
            "headerName": "Brand"
        },
        {
            "field": "serial_no",
            "headerName": "Serial Number"
        },
        {
            "field": "village",
            "headerName": "Village"

        },
        {
            "field": "municipality",
            "headerName": "Municipality"
        }
    ]
    console.log(props.inactiveConsumer)
    return (
        <Paper sx={{ height: 400, maxWidth:"1200px", width:"1000px"}}>
            {props.inactiveConsumer && <DataGrid
                checkboxSelection
                autoPageSize ={true}
                rows={props.inactiveConsumer}
                columns={columName} />
            }
        </Paper>
        // <TableContainer>
        //     <Table sx={{ minWidth: 650 }} aria-label="simple table">
        //         <TableHead>
        //             <TableRow>
        //                 {columName.map((col, index)=>
        //                 <TableCell key={index}>
        //                     {col}
        //                 </TableCell>)}
        //             </TableRow>
        //         </TableHead>
        //         <TableBody>
        //             {
        //              props.inactiveConsumer &&  props.inactiveConsumer.map((cons, index)=>(
        //                     <TableRow key={index}>
        //                         <TableCell>
        //                             {cons.account_no}
        //                         </TableCell>
        //                         <TableCell>
        //                             {cons.consumer_name}
        //                         </TableCell>
        //                         <TableCell>
        //                             {cons.type}
        //                         </TableCell>
        //                         <TableCell>
        //                             {cons.brand}
        //                         </TableCell>
        //                         <TableCell>
        //                             {cons.serial_no}
        //                         </TableCell>
        //                         <TableCell>
        //                             {cons.village}
        //                         </TableCell>
        //                         <TableCell>
        //                             {cons.municipality}
        //                         </TableCell>
        //                     </TableRow>
        //                 ))
        //             }
        //         </TableBody>
        //     </Table>
        // </TableContainer>
    )
}
export default InactiveTable;