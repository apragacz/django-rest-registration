import React, { Component } from 'react';
import TextField from 'material-ui/TextField';

import OKCancelDialog from './OKCancelDialog';
import getFormFieldChangeHandler from './getFormFieldChangeHandler';


export default class LoginDialog extends Component {
  initialState = {
    formData: {
      login: "",
      password: "",
    },
  };
  state = this.initialState;
  handleLoginChange = getFormFieldChangeHandler(this, 'login');
  handlePasswordChange = getFormFieldChangeHandler(this, 'password');

  handleOkClick = () => {
    return this.props.onSubmit(this.state.formData);
  }

  handleClose = () => {
    this.props.onClose();
    this.setState(this.initialState);
  }

  render() {
    const { open } = this.props;
    const {login, password} = this.state.formData;
    return (
      <OKCancelDialog
        title="Sign in"
        open={open}
        onClose={this.handleClose}
        onOkClick={this.handleOkClick}
      >
        <TextField
          name="login"
          value={login}
          onChange={this.handleLoginChange}
          floatingLabelText="Login"
          fullWidth={true}
        />
        <TextField
          name="password"
          type="password"
          value={password}
          onChange={this.handlePasswordChange}
          floatingLabelText="Password"
          fullWidth={true}
        />
      </OKCancelDialog>
    )
  }
}
