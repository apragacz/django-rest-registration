import React, { Component } from 'react';
import TextField from 'material-ui/TextField';

import OKCancelDialog from './OKCancelDialog';
import getFormFieldChangeHandler from './getFormFieldChangeHandler';


export default class AddLinkDialog extends Component {
  initialState = {
    formData: {
      title: "",
      url: "",
    },
  };
  state = this.initialState;
  handleTitleChange = getFormFieldChangeHandler(this, 'title');
  handleUrlChange = getFormFieldChangeHandler(this, 'url');

  handleOkClick = () => {
    return this.props.onSubmit(this.state.formData);
  }

  handleClose = () => {
    this.props.onClose();
    this.setState(this.initialState);
  }

  render() {
    const { open } = this.props;
    const { title, url } = this.state.formData;
    return (
      <OKCancelDialog
        title="Add link"
        open={open}
        onClose={this.handleClose}
        onOkClick={this.handleOkClick}
      >
        <TextField
          name="title"
          value={title}
          onChange={this.handleTitleChange}
          fullWidth={true}
          floatingLabelText="Title"
        />
        <TextField
          name="url"
          type="url"
          value={url}
          onChange={this.handleUrlChange}
          fullWidth={true}
          floatingLabelText="URL"
        />
      </OKCancelDialog>
    )
  }
}
