
import JSONInput from 'react-json-editor-ajrm';
import locale from 'react-json-editor-ajrm/locale/en';

import React, { PureComponent } from 'react';
import service from '../../service';

class EditSettings extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      settings: {},
      editSettings: undefined,
      loading: false,
    }

    this.onChange = this.onChange.bind(this);
    this.onRefresh = this.onRefresh.bind(this);
    this.onSave = this.onSave.bind(this);
  }

  componentDidMount() {
    this.onRefresh();
  }

  onRefresh() {
    this.setState({ loading: true }, async () => {
      const settings = await service.fetchAllSettings();
      if (settings) {
        this.setState({ settings, editSettings: settings, loading: false });
      }
    });
  }

  onSave() {
    if (this.state.editSettings) {
      this.setState({ loading: true }, async () => {
        await service.saveSettings(this.state.editSettings);
        this.onRefresh();
      });
    }
  }

  onChange(content) {
    console.log(content);
    if (content.error) {
      this.setState({ editSettings: undefined });
      return;
    }

    this.setState({ editSettings: content.jsObject })
  }

  renderLoader() {
    const { loading } = this.state;

    if (loading) {
      return <div className="spinner edit-settings__loader"></div>;
    }
  }

  render() {
    return (
      <div className="edit-settings">
        {this.renderLoader()}
        <h4>Settings</h4>
        <div className="edit-settings__wrapper">
          <JSONInput
            placeholder={this.state.settings}
            onChange={this.onChange}
            locale={locale}
            confirmGood={false}
            width='100%'
            height='100%'
          />
        </div>
        <div className="edit-settings__controls">
          <button onClick={this.onRefresh}>Refresh</button>
          <button onClick={this.onSave}>Save Edits</button>
        </div>
      </div>
    )
  }

}

export default EditSettings;