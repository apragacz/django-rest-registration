import BaseService from './BaseService';


export default class LinksService extends BaseService {
  endpointUrl = `${this.serverUrl}links/`;

  list() {
    return this.getJson(`${this.endpointUrl}`);
  }

  add(title, url, authToken) {
    return this.postJson(`${this.endpointUrl}`, {
      title,
      url,
    }, {
      authToken,
    });
  }

  callDetailAction(name, linkId, data, authToken) {
    return this.postJson(`${this.endpointUrl}${linkId}/${name}/`, data, {
      authToken,
    });
  }


  voteUp(linkId, authToken) {
    return this.callDetailAction('vote_up', linkId, null, authToken);
  }

  voteDown(linkId, authToken) {
    return this.callDetailAction('vote_down', linkId, null, authToken);
  }

}
