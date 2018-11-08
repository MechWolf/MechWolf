import React from 'react'
import { ResponsiveXYFrame, XYFrame } from 'semiotic';
import _ from 'lodash';

export default function ({data,times,time_zero}) {
  //Define a 2 minute sliding window for the graphs
  //Start at 0 seconds or 2 minutes before the endpoint, whichever is greater.
  const minimum = Math.max(
    ((Math.max(...times))-time_zero-120), 0
  );
  //end at 2 minutes or the endpoint, whichever is greater.
  const maximum = Math.max(
    ((Math.max(...times)), 120)
  );
  return(
    <ResponsiveXYFrame
      size={[700,300]}
      responsiveWidth={true}
      lines={_.zip(data,times)}
      xAccessor={d => d[1] - time_zero}
      yAccessor={d => d[0]}
      lineStyle={{ stroke: "#00a2ce", fill:"000000" }}
      xExtent={[minimum,maximum]}
      margin={{ left: 80, bottom: 50, right: 10, top: 40 }}
      axes={[
        { orient: 'left', tickFormat: d => d, label: 'Absorbance (AU)', tickSize: 0},
        { orient: 'bottom', tickFormat: d => d, label: 'Time (s)', tickSize: 0 }
      ]}

   />
 );
}
