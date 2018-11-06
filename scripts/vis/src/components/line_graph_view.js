import React from 'react'
import { ResponsiveXYFrame } from 'semiotic';


export default function ({data,time_zero}) {
  return(
    <ResponsiveXYFrame
      size={[700,300]}
      responsiveWidth={true}
      lines={data}
      xAccessor={data => data["timestamp"] - time_zero}
      yAccessor="data"
      lineStyle={{ stroke: "#00a2ce" }}
      margin={{ left: 80, bottom: 50, right: 10, top: 40 }}
      axes={[
        { orient: 'left', tickFormat: d => d, label: 'Absorbance (AU)'},
        { orient: 'bottom', tickFormat: d => d, label: 'Time (s)' }
      ]}

   />
 );
}
