import React, { Component } from 'react';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';

export default class OKDialog extends Component {

  handleClose = () => {
    const { onClose } = this.props;
    onClose();
  };

  render() {
    const { title, open } = this.props;
    const actions = [
      <FlatButton
        label="OK"
        primary={true}
        keyboardFocused={true}
        onClick={this.handleClose}
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
