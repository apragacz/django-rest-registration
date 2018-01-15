import React, { Component } from 'react';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';

export default class OKCancelDialog extends Component {

  handleClose = () => {
    const { onClose } = this.props;
    onClose();
  };

  handleOK = (event) => {
    const {
      onOkClick = () => {},
    } = this.props;
    const p = onOkClick(event);
    if (p && p.then) {
      return p.then(() => {
        this.handleClose();
      });
    } else {
      this.handleClose();
    }
  };

  render() {
    const { title, open } = this.props;
    const actions = [
      <FlatButton
        label="Cancel"
        primary={true}
        onClick={this.handleClose}
      />,
      <FlatButton
        label="OK"
        primary={true}
        keyboardFocused={true}
        onClick={this.handleOK}
      />,
    ];

    return (
      <Dialog
        title={title}
        actions={actions}
        modal={false}
        open={open}
        onRequestClose={this.handleClose}
      >
        {this.props.children}
      </Dialog>
    );
  }
}
