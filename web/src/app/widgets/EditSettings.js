
import JSONInput from 'react-json-editor-ajrm';
import locale from 'react-json-editor-ajrm/locale/en';


import React, { PureComponent } from 'react';
import mqtt from '../../mqtt';

class EditSettings extends PureComponent {

  render() {

    const object = {
      'hello': 'world'
    }

    return (
      <JSONInput
        id="a_unique_id"
        placeholder={object}
        locale={locale}
        height='100%'
      />
    )
  }

}

export default EditSettings;