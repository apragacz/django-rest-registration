import React, { Component } from 'react';
import PropTypes from 'prop-types';

import {
  Table,
  TableBody,
  TableHeader,
  TableHeaderColumn,
  TableRow,
  TableRowColumn,
} from 'material-ui/Table';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import ContentAdd from 'material-ui/svg-icons/content/add';
import ContentRemove from 'material-ui/svg-icons/content/remove';

import AddLinkDialog from '../dialogs/AddLinkDialog';
import FlatButton from 'material-ui/FlatButton/FlatButton';

const style = {
  marginRight: 20,
};


const LoggedLinkActions = ({onVoteUpClick, onVoteDownClick}) => (
  <span>
    <FlatButton
      icon={<ContentAdd />}
      onClick={onVoteUpClick}
    />
    <FlatButton
      icon={<ContentRemove />}
      onClick={onVoteDownClick}
    />
  </span>
);


const LinkRow = ({link, loggedIn, ...propRest}) => (
  <TableRow>
    <TableRowColumn>
      <a href={link.url} target="_blank" rel="noopener noreferrer">
        {link.title}
      </a>
    </TableRowColumn>
    <TableRowColumn>{link.reporter.username}</TableRowColumn>
    <TableRowColumn>{link.vote_rank}</TableRowColumn>
    <TableRowColumn>
      {loggedIn && (
        <LoggedLinkActions {...propRest} />
      )}
    </TableRowColumn>
  </TableRow>
);


const LinkTable = ({linksProps, loggedIn}) => (
  <Table selectable={false}>
    <TableHeader>
      <TableRow>
        <TableHeaderColumn>Title</TableHeaderColumn>
        <TableHeaderColumn>Reporter</TableHeaderColumn>
        <TableHeaderColumn>Vote Rank</TableHeaderColumn>
        <TableHeaderColumn>Actions</TableHeaderColumn>
      </TableRow>
    </TableHeader>
    <TableBody>
      {linksProps.map((linkProps) => (
        <LinkRow
          key={linkProps.link.id}
          loggedIn={loggedIn}
          {...linkProps}
        />
      ))}
    </TableBody>
  </Table>
);


export default class Dashboard extends Component {
  static contextTypes = {
    auth: PropTypes.object,
    services: PropTypes.object,
  }

  state = {
    links: [],
    openAddLinkDialog: false,
  };

  reloadData() {
    const { services } = this.context;
    services.links.list().then((links) => {
      this.setState({ links });
    });
  }

  componentDidMount() {
    this.reloadData();
  }

  handleAddLinkClick = () => {
    this.setState({ openAddLinkDialog: true });
  }

  handleAddLinkDialogClose = () => {
    this.setState({ openAddLinkDialog: false });
  }

  handleAddLinkSubmit = (formData) => {
    const { auth, services } = this.context;
    const { title, url } = formData;
    services.links.add(title, url, auth.token).then(() => {
      this.reloadData();
    });
  }

  render() {
    const { auth, services } = this.context;
    const { links, openAddLinkDialog } = this.state;
    const linksProps = links.map((link) => ({
      link,
      onVoteUpClick: () => {
        services.links.voteUp(link.id, auth.token).then(() => {
          this.reloadData();
        });
      },
      onVoteDownClick: () => {
        services.links.voteDown(link.id, auth.token).then(() => {
          this.reloadData();
        });
      },
    }))
    return (
      <div>
        <LinkTable linksProps={linksProps} loggedIn={!!auth.user} />
        <AddLinkDialog
          open={openAddLinkDialog}
          onClose={this.handleAddLinkDialogClose}
          onSubmit={this.handleAddLinkSubmit}
        />
        { auth.user && (
          <FloatingActionButton style={style} onClick={this.handleAddLinkClick}>
            <ContentAdd />
          </FloatingActionButton>
        )}
      </div>
    );
  }
}
