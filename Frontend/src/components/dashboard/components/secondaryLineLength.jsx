import React, { useState, useEffect } from "react";
import { PieChart } from "@mui/x-charts";
import { Paper, Stack, Typography } from "@mui/material";
import {
    FormControl,
    MenuItem,
    InputLabel
} from "@mui/material";
import Select from "@mui/material/Select";
function SecondaryLineLength(props) {
    const [selected, setSelected] = useState("")
    const substation = props.slLength?.map(sl=>sl.substation_id) || [];
    const filterData = props.slLength?.filter(item => item.substation_id === selected)
    const settings = filterData[0]?.series ? {series:filterData[0].series, hideLegend: true} : null
    const handleChage = (event) =>{
        setSelected(event.target.value)
    }
    useEffect(()=>{
        if (!selected & substation.length > 0){
            setSelected(substation[0])}
        },[substation, selected])
    return (
        <Paper sx={{height:props.isMobile? 320 : 340,width:"100%" ,border:"1px solid grey"}}>
            <Stack direction="row" justifyContent="space-between">
                <Typography margin={3}>
                    Secondary Line Length(Meters)
                </Typography>
                <FormControl>
                <InputLabel>
                    Secondary Line Length
                </InputLabel>
                {substation && <Select
                value={selected}
                onChange={handleChage}
                >
                {substation?.map((s, index)=>(
                    <MenuItem key={index} value={s}>{s}</MenuItem>
                ))}
                </Select>}
            </FormControl>

            </Stack>
            
            {settings && <PieChart
            height={props.isMobile? 200 : 250}
            width={props.isMobile? 200 : 300}
            {...settings} />
            }
        </Paper>
    )
}

export default SecondaryLineLength;