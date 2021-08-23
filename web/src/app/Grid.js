import React, { PureComponent } from 'react'
import { Responsive, WidthProvider} from "react-grid-layout";

import { WidgetTypes } from './models';

const ResponsiveGridLayout = WidthProvider(Responsive);

export default class Grid extends PureComponent {
  constructor(props) {
    super(props);

    this.state = {
      edit: false,
      items: [],
      itemCounter: 0,
      gridProperties: {
        autoSize: true,
        compactType: null,
        margin: [10, 10],
        containerPadding: [10, 10],
        isDraggable: false,
        isResizable: false,
        onLayoutChange: function() {},
      }
    };

    this.onItemAdd = this.onItemAdd.bind(this);
    this.onItemRemove = this.onItemRemove.bind(this);
    this.onChangeMode = this.onChangeMode.bind(this);
    this.onLayoutChange = this.onLayoutChange.bind(this);
  }

  onItemAdd(type) {
    const { itemCounter, items } = this.state; 
    const defaults = WidgetTypes[type];
    if (defaults) {
      const newItemCounter = itemCounter + 1;
      items.push({
        settings: { 
          ...defaults.settings, 
          type, 
          i: newItemCounter.toString()
        },
        Component: defaults.Component,
      });

      this.setState({
        items,
        itemCounter: newItemCounter
      });
    }
  }

  onItemRemove(index) {
    const { items } = this.state;
    items.splice(index, 1);
    this.setState({ items });
  }

  onChangeMode(checked) {
    const { gridProperties } = this.state;
    if (checked) {
      gridProperties.isDraggable = true;
      gridProperties.isResizable = true;
      this.setState({ edit: true, gridProperties });
    } else {
      gridProperties.isDraggable = false;
      gridProperties.isResizable = false;
      this.setState({ edit: false, gridProperties });
    }
  }

  onLayoutChange(layout) {
    this.state.gridProperties.onLayoutChange(layout);
  }

  renderWidgets() {
    const { items, edit } = this.state;

    let widgetClasses = 'widget';
    if (!edit) {
      widgetClasses += ' react-control-hide';
    }

    return items.map((item, i) => {
      return (
        <div
          className={widgetClasses}
          key={item.settings.i}
          data-grid={item.settings}
        >
          <div
            className="react-remove-handle"
            onClick={() => this.onItemRemove(i)}
          >
            x
          </div>
          <item.Component edit={edit} />
        </div>
      );
    });
  }

  renderMenu() {
    return (
      <div className="grid__menu">

        <select onChange={(event) => this.onItemAdd(event.target.value)}>
          <option value="disable">Disable Services</option>
          <option value="toggle">Toggle Services</option>
          {/*<option value="manual_watering">Manual Watering</option>*/}
          {/*<option value="train_soil">Train Soil Model</option>*/}
          {/*<option value="select_soil">Select Soil Model</option>*/}
          <option value="edit_settings">Edit Settings</option>
          <option value="global_settings">Global Settings</option>
          <option value="server_stats">Server Statistics</option>
          <option value="live_stream">Live Stream</option>
          <option value="alarms">Alarms</option>
        </select>

        <div className="switcher">
          <label className="switch">
            <input
              type="checkbox"
              checked={this.state.edit}
              onChange={() => {}}
              onClick={(event) => this.onChangeMode(event.target.checked)}
            />
            <span className="slider"></span>
          </label>
          Edit Mode
        </div>
      </div>
    )
  }

  render() {
    return (
      <div className="grid">
        {this.renderMenu()}
        <div className="grid__layout">
          <ResponsiveGridLayout
            onLayoutChange={this.onLayoutChange}
            {...this.state.gridProperties}
          >
              {this.renderWidgets()}
          </ResponsiveGridLayout>
        </div>
      </div>
    )
  }
}
