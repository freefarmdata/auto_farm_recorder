import React, { PureComponent } from 'react';
import ReactECharts from 'echarts-for-react';

import mqtt from '../../mqtt.js';
import service from '../../service';

function appendPointToObject(object, point, max) {
  if (!object[point.board]) {
    object[point.board] = {};
  }

  if (!object[point.board][point.metric]) {
    object[point.board][point.metric] = {}
  }

  if (!object[point.board][point.metric][point.sensor]) {
    object[point.board][point.metric][point.sensor] = []
  }

  object[point.board][point.metric][point.sensor].unshift({
    timestamp: point.timestamp * 1000,
    value: point.value
  })

  if (object[point.board][point.metric][point.sensor].length > max) {
    object[point.board][point.metric][point.sensor].pop();
  }

  return object;
}

export default class Sensors extends PureComponent {

    constructor(props) {
        super(props);
    
        this.state = {
          data: {},
          boards: [],
          metrics: [],
          selectedBoard: '',
          selectedMetric: '',
          loading: false,
        };
    
        this.getOptions = this.getOptions.bind(this);
        this.fetchBoards = this.fetchBoards.bind(this);
        this.onData = this.onData.bind(this);
    }
    
      componentDidMount() {
        this.fetchBoards();
        mqtt.subscribe('web/board', this.onData);
      }
    
      componentWillUnmount() {
        mqtt.unsubscribe('web/board', this.onData);
      }

      onData(rawdata) {
        let { data } = this.state;

        const parsed = JSON.parse(rawdata);

        data = appendPointToObject(data, parsed, 50);

        this.setState({ data: {...data} });
      }

      fetchBoards() {
        this.setState({ loading: true }, async () => {
          const settings = await service.fetchAllSettings();
          this.setState({
            boards: settings?.mqtt_board?.boards || [],
            metrics: settings?.mqtt_board?.metrics || [],
            selectedBoard: settings?.mqtt_board?.boards[0] || '',
          }, async () => {
            const { boards, metrics } = this.state;
            let data = await service.fetchLastDataPoints(boards, metrics.length*50);
            data = data?.reduce((object, point) => {
              return appendPointToObject(object, point, 50);
            }, {});
            this.setState({ data, loading: false });
          });
        });
      }

      getOptions() {
        const { selectedBoard, selectedMetric, data } = this.state;

        const telem = data?.[selectedBoard]?.[selectedMetric] || {};

        const series = Object.keys(telem).map(sensor => {
          const points = (telem[sensor] || {}).map(point => {
            return [ point.timestamp, point.value ]
          });

          return {
            name: `${selectedMetric}: Sensor ${sensor}`,
            data: points,
            type: 'line',
            smooth: true,
          }
        });

        return {
          grid: {
            left: 40,
            right: 10,
            top: 20,
            bottom: 20,
          },
          xAxis: {
            label: 'Timestamp',
            type: 'time',
          },
          yAxis: {
            label: 'Value'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              animation: false
            }
          },
          series: series,
        }
      }

      renderLoading() {
        const { loading } = this.state;
    
        if (loading) {
          return <div className="spinner sensors__loader"></div>
        }
      }

      renderSelections() {
        const { boards, metrics, selectedBoard, selectedMetric } = this.state;

        return (
          <div className="sensors__selection">
            <select value={selectedBoard} onChange={(event) => {
              this.setState({ selectedBoard: event.target.value, selectedMetric: '' })
            }}>
              {boards.map((board, i) => {
                return (
                  <option key={i} value={board}>
                    {board}
                  </option>
                )
              })}
            </select>
            <select value={selectedMetric}  onChange={(event) => {
              this.setState({ selectedMetric: event.target.value })
            }}>
              {metrics.map((metric, i) => {
                return (
                  <option key={i} value={metric}>
                    {metric}
                  </option>
                )
              })}
            </select>
          </div>
        )
      }

      renderData() {
        return (
          <ReactECharts 
            className="sensors__graph"
            option={this.getOptions()}
          />
        )
      }

      render() {
        return (
          <div className="sensors">
            <h4>Sensors</h4>
            {this.renderLoading()}
            <div className="sensors__container">
              {this.renderSelections()}
              {this.renderData()}
            </div>
          </div>
        );
      }

}