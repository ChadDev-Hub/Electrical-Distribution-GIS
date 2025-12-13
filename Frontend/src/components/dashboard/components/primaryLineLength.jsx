import React, { useEffect, useState } from "react";
import { Box, Stack } from "@mui/material";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import { PieChart } from "@mui/x-charts";
import Paper from '@mui/material/Paper';
import {Typography} from "@mui/material";
function PrimarLineLength({plLength, isMobile}){
    //  SELECTED SUBSTATION 
    const [selected, setSelected] = useState("");
    const substation = plLength?.map(d=>d.substation) || [];
    const filterData = plLength?.filter(item=>item.substation === selected);
    // FILTERING THE DATA FOR THE SELECTED SUBSTATION 
    const setting = filterData[0]?.series ? {"series": filterData[0].series} : null;
    function handleChange(event){
        setSelected(event.target.value)
    }
    useEffect(()=>{
        if (!selected & substation.length > 0){
        setSelected(substation[0])}
    },[substation, selected])
    return(
        <Paper sx={{width:"100%", height:isMobile? 320 : 340, border:"1px solid grey"}}>
            <Stack direction="row" justifyContent="space-between">
                <Typography sx={{m:2, fontWeight:"bold"}}>
                Primary Line Length (Meters)
                </Typography>
                <FormControl>
                <InputLabel>Substation</InputLabel>
                {substation && <Select
                defaultValue="CIPC0001"
                value={selected}
                label="Substation"
                onChange={handleChange}>
                    {substation?.map((d, index)=>(
                        <MenuItem key={index} value={d}>{d}</MenuItem>
                    ))}
                </Select>}
            </FormControl>
                
            </Stack>
            {setting && <PieChart
            height={isMobile? 200 : 250}
            width={isMobile? 200 : 300}
            title="Primary Line Length(meters)"
            {...setting}
            hideLegend={true}
            />}
        </Paper>
    )
}

export default PrimarLineLength