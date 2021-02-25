import React, { Component } from 'react';
import { Router, Route } from 'react-router-dom'
import {createBrowserHistory} from 'history';
import PropTypes from 'prop-types';

import AppBar from 'material-ui/AppBar';
import IconButton from 'material-ui/IconButton';
import IconMenu from 'material-ui/IconMenu';
import MenuItem from 'material-ui/MenuItem';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import MoreVertIcon from 'material-ui/svg-icons/navigation/more-vert';
import FlatButton from 'material-ui/FlatButton/FlatButton';

import LoginDialog from './dialogs/LoginDialog';
import RegisterDialog from './dialogs/RegisterDialog';
import AuthService from './services/AuthService';
import LinksService from './services/LinksService';
import Dashboard from './views/Dashboard';
import VerifyUser from './views/VerifyUser';

const history = createBrowserHistory();


class MenuContainer extends Component {
  static muiName = 'IconMenu';

  render() {
    const {
      iconButtonElement = (
        <IconButton><MoreVertIcon /></IconButton>
      ),
    } = this.props;
    return (
      <IconMenu
        {...this.props}
        iconButtonElement={iconButtonElement}
        targetOrigin={{horizontal: 'right', vertical: 'top'}}
        anchorOrigin={{horizontal: 'right', vertical: 'top'}}
      >
        {this.props.children}
      </IconMenu>
      );
  }
}

class NotLoggedMenu extends Component {

  render() {
    const {
      onSignInClick,
      onSignUpClick,
      ...propsRest
    } = this.props;
    return (
      <MenuContainer{...propsRest}>
        <MenuItem primaryText="Sign up" onClick={onSignUpClick} />
        <MenuItem primaryText="Sign in" onClick={onSignInClick} />
      </MenuContainer>
    );
  }
}

class LoggedMenu extends Component {
  static contextTypes = {
    auth: PropTypes.object,
  }

  render() {
    const {
      onSignOutClick,
      ...propsRest
    } = this.props;
    const { auth } = this.context;
    return (
      <MenuContainer
        {...propsRest}
        iconButtonElement={<FlatButton label={auth.user.username} />}
      >
        <MenuItem primaryText="Sign out" onClick={onSignOutClick} />
      </MenuContainer>
    );
  }
}


class AppContainer extends Component {
  static childContextTypes = {
    auth: PropTypes.object,
    services: PropTypes.object,
    history: PropTypes.object,
  };

  initialState = {
    auth: {
      user: null,
      token: null,
    },
    openDialogs: {
      login: false,
      register: false,
    }
  };

  state = this.initialState;

  services = {
    auth: new AuthService(),
    links: new LinksService(),
  };

  getChildContext() {
    const { auth } = this.state;
    const { services } = this;
    return { auth, services, history };
  }

  getDialogOpenCloseHandler(name, open) {
    return () => {
      this.setState((prevState) => {
        const openDialogsUpdate = {}
        openDialogsUpdate[name] = open;
        return {
          openDialogs: {
            ...prevState.openDialogs,
            ...openDialogsUpdate,
          }
        }
      });
    }
  }

  getDialogOpenHandler(name) {
    return this.getDialogOpenCloseHandler(name, true);
  }

  getDialogCloseHandler(name) {
    return this.getDialogOpenCloseHandler(name, false);
  }

  handleSignUpClick = this.getDialogOpenHandler('register');

  handleSignInClick = this.getDialogOpenHandler('login');

  handleSignOutClick = () => {
    this.setState({
      auth: this.initialState.auth,
    });
  }

  handleLoginSubmit = (formData) => {
    return this.services.auth.getAuthTokenWithUserProfile(
        formData.login, formData.password).then((auth) => {
      this.setState({ auth });
    })
  }

  handleRegisterSubmit = (formData) => {
    const {
      username,
      email,
      firstName,
      lastName,
      password,
      passwordConfirm,
    } = formData;
    return this.services.auth.register(
      username, email, firstName, lastName, password, passwordConfirm);
  }

  render() {
    const {
      auth,
      openDialogs,
    } = this.state;
    const loggedProps = {
      onSignOutClick: this.handleSignOutClick,
    };
    const notLoggedProps = {
      onSignUpClick: this.handleSignUpClick,
      onSignInClick: this.handleSignInClick,
    };
    return (
      <MuiThemeProvider>
        <div>
          <AppBar
            title="Shared links"
            iconElementRight={auth.user ? (
              <LoggedMenu {...loggedProps} />
            ) : (
              <NotLoggedMenu {...notLoggedProps} />
            )}
          />
          <LoginDialog
            open={openDialogs.login}
            onClose={this.getDialogCloseHandler('login')}
            onSubmit={this.handleLoginSubmit}
          />
          <RegisterDialog
            open={openDialogs.register}
            onClose={this.getDialogCloseHandler('register')}
            onSubmit={this.handleRegisterSubmit}
          />
          <main>
            {this.props.children}
          </main>
        </div>
      </MuiThemeProvider>
    );
  }
}

class App extends Component {
  render() {
    return (
        <Router history={history}>
          <AppContainer>
            <Route path="/" component={Dashboard}/>
            <Route path="/verify-user/" component={VerifyUser}/>
          </AppContainer>
        </Router>
    );
  }
}

export default App;
