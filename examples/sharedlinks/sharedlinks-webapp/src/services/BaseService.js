export default class BaseService {
  serverUrl = 'http://localhost:8000/api/'

  buildHeaders(headers, options) {
    if (options && options.authToken) {
      return Object.assign(headers, {
        Authorization: `Token ${options.authToken}`,
      });
    }
    return headers;
  }

  handleJsonResponse(responsePromise) {
    return responsePromise
    .catch(() => {
      throw new Error("Communication error");
    })
    .then((response) => {
      if (response.status >= 400) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    });
  }

  getJson(url, options) {
    const headers = this.buildHeaders({
      Accept: 'application/json',
    }, options);
    const responsePromise = fetch(url, {
      method: 'GET',
      headers,
    });
    return this.handleJsonResponse(responsePromise);
  }

  postJson(url, data, options) {
    const headers = this.buildHeaders({
      Accept: 'application/json',
      'Content-Type': 'application/json',
    }, options);
    const responsePromise = fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    return this.handleJsonResponse(responsePromise);
  }
}
