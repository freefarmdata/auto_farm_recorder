
import JSONInput from 'react-json-editor-ajrm';
import locale from 'react-json-editor-ajrm/locale/en';

import React, { PureComponent } from 'react';
import service from '../../service';

class EditSettings extends PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      settings: {},
      loading: true,
    }
  }

  async componentDidMount() {
    const settings = await service.fetchAllSettings();
    this.setState({ settings, loading: false })
  }

  render() {
    const { loading } = this.state;

    if (loading) {
      return <div className="spinner"></div>;
    }

    return (
      <JSONInput
        placeholder={this.state.settings}
        locale={locale}
        confirmGood={false}
        width='100%'
        height='100%'
      />
    )
  }

}

export default EditSettings;