import React, { Component } from 'react';
import TextField from 'material-ui/TextField';

import OKCancelDialog from './OKCancelDialog';
import getFormFieldChangeHandler from './getFormFieldChangeHandler';


export default class RegisterDialog extends Component {
  initialState = {
    formData: {
      username: "",
      email: "",
      firstName: "",
      lastName: "",
      password: "",
      passwordConfirm: "",
    },
  };
  state = this.initialState;
  handleUsernameChange = getFormFieldChangeHandler(this, 'username');
  handleEmailChange = getFormFieldChangeHandler(this, 'email');
  handleFirstNameChange = getFormFieldChangeHandler(this, 'firstName');
  handleLastNameChange = getFormFieldChangeHandler(this, 'lastName');
  handlePasswordChange = getFormFieldChangeHandler(this, 'password');
  handlePasswordConfirmChange = getFormFieldChangeHandler(this, 'passwordConfirm');

  handleOkClick = () => {
    return this.props.onSubmit(this.state.formData);
  }

  handleClose = () => {
    this.props.onClose();
    this.setState(this.initialState);
  }

  render() {
    const { open } = this.props;
    const {
      username,
      email,
      firstName,
      lastName,
      password,
      passwordConfirm,
    } = this.state.formData;
    return (
      <OKCancelDialog
        title="Sign up"
        open={open}
        onClose={this.handleClose}
        onOkClick={this.handleOkClick}
      >
        <TextField
          name="username"
          value={username}
          onChange={this.handleUsernameChange}
          floatingLabelText="Username"
          fullWidth={true}
        />
        <TextField
          name="email"
          type="email"
          value={email}
          onChange={this.handleEmailChange}
          floatingLabelText="E-mail"
          fullWidth={true}
        />
        <TextField
          name="first-name"
          value={firstName}
          onChange={this.handleFirstNameChange}
          floatingLabelText="First Name"
        />
        <TextField
          name="last-name"
          value={lastName}
          onChange={this.handleLastNameChange}
          floatingLabelText="Last Name"
        />
        <TextField
          name="password"
          type="password"
          value={password}
          onChange={this.handlePasswordChange}
          floatingLabelText="Password"
          fullWidth={true}
        />
        <TextField
          name="password-change"
          type="password"
          value={passwordConfirm}
          onChange={this.handlePasswordConfirmChange}
          floatingLabelText="Password Confirmation"
          fullWidth={true}
        />
      </OKCancelDialog>
    )
  }
}
