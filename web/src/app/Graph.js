import React, { Component } from 'react';
import moment from 'moment';
import EChart from 'echarts-for-react';

class Graph extends Component {
  constructor(props) {
    super(props);
    this.state = {
      options: undefined,
      startTime: undefined,
      endTime: undefined,
    }

    this.onRefresh = this.onRefresh.bind(this);
  }

  componentDidMount() {
    this.setGraphOptions();
  }

  componentWillUnmount() {

  }

  onRefresh() {
    const { startTime, endTime } = this.state;

    if (startTime && endTime && endTime.isAfter(startTime)) {
      console.log('refresh')
    }
  }

  setGraphOptions() {
    const options = {
      grid: {
        top: 50,
        bottom: 50,
        left: 50,
        right: 50
      },
      tooltip: {
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      },
      yAxis: {
          type: 'value'
      },
      series: [{
          data: [150, 230, 224, 218, 135, 147, 260],
          type: 'line',
          smooth: true,
      }],
      animationEasing: 'elasticOut',
      animationDelayUpdate: (idx) => idx,
    };

    this.setState({ options: options });
  }

  renderGraph() {
    if (this.state.options) {
      return (
        <EChart className="graphs__graph" option={this.state.options} />
      )
    }
  }

  renderOptions() {
    return (
      <div className="graphs__options">
        <input
          type="datetime-local"
          onChange={(e) => {
            this.setState({ startTime: moment(e.target.value) });
          }}
        />
        <input
          type="datetime-local"
          onChange={(e) => {
            this.setState({ endTime: moment(e.target.value) });
          }}
        />
        <button
          onClick={this.onRefresh}
        >
          Refresh
        </button>
      </div>
    );
  }

  render() {
    return (
      <div className="graphs">
        <h2>Graphed Data</h2>
        <div className="graphs__container">
          {this.renderOptions()}
          {this.renderGraph()}
        </div>
      </div>
    );
  }
}

export default Graph;