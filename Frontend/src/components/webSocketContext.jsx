import React, { createContext, useContext } from "react";

export const WSContext = createContext(null);
export function useWS(){
    return(useContext(WSContext))
}