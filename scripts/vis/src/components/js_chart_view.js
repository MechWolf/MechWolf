import React from 'react';
import {Scatter} from 'react-chartjs-2';
import _ from 'lodash';

export default function ({data,times,time_zero}) {
  //Define a 2 minute sliding window for the graphs
  //Start at 0 seconds or 2 minutes before the endpoint, whichever is greater.
  const minimum = Math.max(
    (Math.max(...times)-time_zero-60), 0
  );
  //end at 2 minutes or the endpoint, whichever is greater.
  const maximum = Math.max(
    (Math.max(...times)-time_zero), 60
  );
  const zipped = _.zip(times,data)
  const graph = zipped.map( a => { return {x:(a[0] - time_zero), y:a[1]}; })
  const filtered_graph = graph.filter( point => point.x < maximum && point.x > minimum )
  return(
    <div>
      <Scatter data={
        { datasets: [
            {label: "Chart", data: filtered_graph, showLine: true, fill: false}
          ],
          options: {
            scales: {
              xAxes: [{
                  display:true,
                  ticks: {
                    min: minimum,
                    max: maximum
                  }
              }]
            }
          }
        }
      } />
    </div>
 );
}
