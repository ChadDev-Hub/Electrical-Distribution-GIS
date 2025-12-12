import React, { useState } from "react";
import { Box, Stack } from "@mui/material";
import { BarChart } from "@mui/x-charts";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import { PieChart } from '@mui/x-charts/PieChart';
import Paper from '@mui/material/Paper';
import {Typography} from "@mui/material";
function PrimarLineLength({plLength, isMobile}){
    const [category, setCategory] = useState("CIPC0001")
    const substation = plLength?.map(d=>d.substation) || []
    const data = plLength?.filter(item=>item.substation === category)
    const  filterData = [
        {label: "Single Phase", value: data[0]?.single_phase},
        {label: "V Phase", value: data[0]?.v_phase},
        {label: "Three Phase", value: data[0]?.three_phase}
    ]
    console.log(filterData)
    function handleChange(event){
        setCategory(event.target.value)
    }
    return(
        <Paper sx={{width:"100%", height:isMobile? "300px": "400px", border:"1px solid grey"}}>
            <Stack direction="row" justifyContent="space-between">
                <Typography sx={{m:2, fontWeight:"bold"}}>
                Primary Line Length (Meters)
                </Typography>
                <FormControl>
                <InputLabel>Substation</InputLabel>
                <Select
                defaultValue="CIPC0001"
                value={category}
                label="Substation"
                onChange={handleChange}>
                    {substation?.map((d)=>(
                        <MenuItem value={d}>{d}</MenuItem>
                    ))}
                </Select>
            </FormControl>
                
            </Stack>
            
            <PieChart
            height={isMobile? 200 : 300}
            width={isMobile? 200 : 300}
            title="Primary Line Length(meters)"
            series={[{
                data: filterData,
                highlightScope: { fade: 'global', highlight: 'item' },
                faded: { innerRadius: 30, additionalRadius: -30, color: 'gray' }
            }]}
            />
        </Paper>
    )
}

export default PrimarLineLength