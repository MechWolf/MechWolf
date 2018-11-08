import React from 'react'
import { ResponsiveXYFrame, XYFrame } from 'semiotic';
import _ from 'lodash';

export default function ({data,times,time_zero}) {
  return(
    <XYFrame
      size={[700,300]}
      responsiveWidth={true}
      lines={_.zip(data,times)}
      xAccessor={d => d[1] - time_zero}
      yAccessor={d => d[0]}
      lineStyle={{ stroke: "#00a2ce" }}
      margin={{ left: 80, bottom: 50, right: 10, top: 40 }}
      axes={[
        { orient: 'left', tickFormat: d => d, label: 'Absorbance (AU)', tickSize: 0},
        { orient: 'bottom', tickFormat: d => d, label: 'Time (s)', tickSize: 0 }
      ]}

   />
 );
}
