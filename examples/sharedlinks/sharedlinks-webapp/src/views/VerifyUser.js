import React, { Component } from 'react';
import PropTypes from 'prop-types';
import urlParse from 'url-parse';

import OKDialog from '../dialogs/OKDialog';


class VerifyUserOkDialog extends Component {
  render() {
    return (
      <OKDialog {...this.props}>
        User Verification OK
      </OKDialog>
    );
  }
}


class VerifyUserFailedDialog extends Component {
  handleClose() {
  }

  render() {
    return (
      <OKDialog {...this.props}>
        User Verification failed!
      </OKDialog>
    );
  }
}


export default class VerifyUser extends Component {
  static contextTypes = {
    history: PropTypes.object,
    services: PropTypes.object,
  };

  state = {
    openDialogs: {
      ok: false,
      failed: false,
    },
  };

  componentDidMount() {
    const { query } = urlParse(window.location.href, true);
    const { services } = this.context;
    const {
      user_id: userId,
      timestamp,
      signature,
    } = query;
    services.auth.verifyUser(userId, timestamp, signature).then(() => {
      this.setState((prevState) => ({
        openDialogs: {
          ...prevState.openDialogs,
          ok: true,
        },
      }));
    }).catch(() => {
      this.setState((prevState) => ({
        openDialogs: {
          ...prevState.openDialogs,
          failed: true,
        },
      }));
    });
  }

  handleOkClose = () => {
    const { history } = this.context;
    history.push('/');
  };

  handleFailedClose = () => {
    this.setState((prevState) => ({
      openDialogs: {
        ...prevState.openDialogs,
        failed: false,
      },
    }));
  };

  render() {
    const { openDialogs } = this.state;
    return (
      <div>
        <VerifyUserOkDialog open={openDialogs.ok} onClose={this.handleOkClose} />
        <VerifyUserFailedDialog open={openDialogs.failed} onClose={this.handleFailedClose} />
      </div>
    )
  }
}
