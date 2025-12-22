import React, { useState } from "react";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import { createFilterOptions } from "@mui/material/Autocomplete";
import { useMap } from "react-leaflet";
import { marker } from "leaflet";
const filterOptions = createFilterOptions({
  limit: 10,
  stringify: (option) => option.label,
});

function SearchConsumer(props){
    const [value, setValue] = useState(null)
    const map = useMap()
    const handleChange = (event ,newValue) =>{
        setValue(newValue); // always update the input, even if null


        
        setValue(newValue)
        if (!newValue) return;
        const marker = props.markerRefs.current[newValue.id]
        if (props.clusterGroupRef.current.zoomToShowLayer) {
        props.clusterGroupRef.current.zoomToShowLayer(marker, () => {
            map.flyTo(marker.getLatLng(), 18);
            marker.openPopup();
        });
    } else {
        map.flyTo(marker.getLatLng(), 18);
        marker.openPopup();
    }
        
    }
    return(
        <Autocomplete
        value={value}
        onChange={handleChange}
        clearOnEscape
        sx={{ position:"absolute", top: 10, left: 50, width: props.isMobile ? 230 : 300 , zIndex:500}}
        getOptionLabel={(o) => o.label}
        filterOptions={filterOptions}
        options={props.options}
        renderInput={(params)=>(<TextField sx={{borderRadius: 80, height: 10}} {...params}  label="Search Consumer Meter"/>)}
        />
    )
}
export default SearchConsumer;