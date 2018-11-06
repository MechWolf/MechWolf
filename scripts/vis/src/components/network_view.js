import React, { Component } from 'react';
import { connect } from 'react-redux';
import { fetchCurrentApparatus } from '../actions'
import { ResponsiveNetworkFrame, NetworkFrame } from 'semiotic';
import dagre from 'dagre';

class NetworkView extends Component {
  componentDidMount() {
    this.props.fetchCurrentApparatus();
  }

  render() {

    if (!this.props.current_apparatus){
      return (<div>loading</div>);
    }

    const nodes = this.props.current_apparatus.nodes
    const edges = this.props.current_apparatus.edges
    // Create a new directed graph
    var g = new dagre.graphlib.Graph();

    // Set an object for the graph label
    g.setGraph({});
    g.setDefaultNodeLabel( function() { return {width:25, height:300};} );
    g.setDefaultEdgeLabel(function() { return {color: "#b3331d", weight: 3}; });
    nodes.map(node => g.setNode(node))
    edges.map(edge => g.setEdge(edge.source, edge.target))

    dagre.layout(g, {rankdir: 'BT'})

    console.log(g);

    return(
        <NetworkFrame
        size={[700, 500]}
        graph={g}
        networkType={{ type: "dagre", zoom: true }}
        nodeStyle={{ fill: "#6a57b6", stroke: "black" }}
        edgeType={{type: 'ribbon'}}
        edgeStyle={d => ({
          stroke: d.color,
          fill: "none",
          strokeWidth: d.weight,
          strokeDasharray: '5,5',
          opacity: 0.6,
        })}
        margin={10}
        nodeLabels={true}
        //hoverAnnotation={true}
        //tooltipContent={d => d.id}
      />
    );
  }

}

function mapStateToProps(state) {
  return {current_apparatus: state.current_apparatus};
}

export default connect(mapStateToProps, { fetchCurrentApparatus })(NetworkView);
