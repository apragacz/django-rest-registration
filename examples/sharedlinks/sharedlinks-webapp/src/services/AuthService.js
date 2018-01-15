import BaseService from './BaseService';


export default class AuthService extends BaseService {
  login(login, password) {
    return this.postJson(`${this.serverUrl}accounts/login/`, {
      login,
      password,
    }).then((responseData) => responseData.token);
  }

  getProfile(authToken) {
    return this.getJson(`${this.serverUrl}accounts/profile/`, {
      authToken,
    });
  }

  getAuthTokenWithUserProfile(login, password) {
    return this.login(login, password).then((token) => {
      return this.getProfile(token).then((user) => ({
        token,
        user,
      }));
    });
  }

  register(username, email, firstName, lastName, password, passwordConfirm) {
    return this.postJson(`${this.serverUrl}accounts/register/`, {
      username,
      email,
      first_name: firstName,
      last_name: lastName,
      password,
      password_confirm: passwordConfirm,
    });
  }

  verifyUser(userId, timestamp, signature) {
    return this.postJson(`${this.serverUrl}accounts/verify-registration/`, {
      user_id: userId,
      timestamp,
      signature,
    });
  }
}
