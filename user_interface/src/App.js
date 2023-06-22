import './App.css';
import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { getUsers, getRecommendedBooks } from './apis/bookRecommenderApi';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import { Typography } from '@mui/material';

class App extends React.Component {
  state = {
    selectedUser: "",
    booksByCollaborativeFiltering: [],
    booksByPopularity: [],
    userIds: [],
    currentUserRatings: [],
    evaluation: {},
    downloadingMessage: null
  }


  lowGridSettings = {
    height: 56,
    padding: 3,
    overflow: 'auto'
  }

  mediumGridSettings = {
    ...this.lowGridSettings,
    height: 345,
  }

  highGridSettings = {
    ...this.lowGridSettings,
    height: 700,
  }


  componentDidMount() {
    this.setState({ downloadingMessage: 'Downloading users' }, () => {
      getUsers().then(response => {
        this.setState({
          userIds: response.data.user_ids,
        });
      }).catch(err => console.log(err)).finally(() => this.setState({ downloadingMessage: '' }));
    })
  }

  getUserSelector() {
    return (
      <FormControl style={{ width: '100%' }}>
        <InputLabel id="user_id_input">User Id</InputLabel>
        <Select
          labelId="user_id_input"
          id="user_id_select"
          value={this.state.selectedUser}
          label="User Id"
          onChange={(event) => this.selectedUserChanged(event.target.value)}
        >
          {
            this.state.userIds?.length && this.state.userIds.map(userId => (
              <MenuItem key={userId} value={userId}>{userId}</MenuItem>
            ))
          }
        </Select>
      </FormControl >
    )
  }

  selectedUserChanged(selectedUser) {
    if (selectedUser) {
      this.setState({ downloadingMessage: `Downloading user: ${selectedUser}` }, () => {
        getRecommendedBooks(selectedUser).then(response => {
          this.setState({
            booksByCollaborativeFiltering: response.data.collaborative_filtering,
            booksByPopularity: response.data.popularity_based,
            selectedUser: selectedUser,
            currentUserRatings: response.data.current_user_ratings,
            evaluation: response.data.evaluation,
            downloadingMessage: ''
          })
        }).catch(err => console.log(err)).finally(() => this.setState({ downloadingMessage: '' }));
      })
    }
  }

  showRecommendations() {
    let booksByCollaborativeFiltering = this.state.booksByCollaborativeFiltering.map(item => ({
      ...item, source: "Collaborative"
    }));
    let booksByPopularity = this.state.booksByPopularity.map(item => ({
      ...item, source: "Popularity-Based"
    }));

    let recommendations = booksByCollaborativeFiltering.concat(booksByPopularity).slice(0, 10)

    return (
      <Paper>
        <TableContainer component={Paper}>
          <Table size="small" aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell>Order</TableCell>
                <TableCell>ISBN</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Author</TableCell>
                <TableCell>Score</TableCell>
                <TableCell>Source</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recommendations?.map((book, idx) => (
                <TableRow
                  key={book.isbn}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell component="th" scope="row">{idx + 1}</TableCell>
                  <TableCell>{book.isbn}</TableCell>
                  <TableCell>{book.bookTitle}</TableCell>
                  <TableCell>{book.bookAuthor}</TableCell>
                  <TableCell>{book.score.toFixed(3)}</TableCell>
                  <TableCell>{book.source}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    )
  }

  showCurrentUserRatings() {
    let ratings = this.state.currentUserRatings;

    return (
      <Paper>
        <TableContainer component={Paper}>
          <Table size="small" aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell>Order</TableCell>
                <TableCell>ISBN</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Author</TableCell>
                <TableCell>Rating</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {ratings?.map((book, idx) => (
                <TableRow
                  key={book.isbn}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell component="th" scope="row">{idx + 1}</TableCell>
                  <TableCell>{book.isbn}</TableCell>
                  <TableCell>{book.bookTitle}</TableCell>
                  <TableCell>{book.bookAuthor}</TableCell>
                  <TableCell>{book.rating}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    )
  }

  getEvaluations() {
    if (!this.state.evaluation)
      return null

    let { error, message, ...rest } = this.state.evaluation;

    return (
      <>
        {
          error ?
            <Typography>ERROR: {error}</Typography>
            : null
        }
        {
          message ?
            <Typography>Message: {message}</Typography>
            : null
        }
        {
          Object.keys(rest).map(key => (
            <Typography key={key}>{this.prettifyKey(key)}: {rest[key].toFixed(3)}</Typography>
          ))
        }
      </>
    )
  }

  prettifyKey(key) {
    return key.toLowerCase().split('_').map(key_part => key_part.charAt(0).toUpperCase() + key_part.substring(1)).join(' ')
  }

  render() {
    return (
      <div className="App" >
        <Box sx={{ flexGrow: 1 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Paper elevation={2} style={this.lowGridSettings}>
                <Grid container item>
                  <Grid item xs={3}>
                    <Typography variant="h5">Select User</Typography>
                  </Grid>
                  <Grid item xs={3}>
                    {this.getUserSelector()}
                  </Grid>
                  <Grid item xs={1}>
                  </Grid>
                  <Grid item xs={5}>
                    {
                      this.state.downloadingMessage ?
                        <Typography style={{ color: "red" }}>{this.state.downloadingMessage}</Typography>
                        :
                        null
                    }
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
            <Grid item xs={6}>
              <Paper elevation={2} style={this.highGridSettings}>
                <Grid container item >
                  <Grid item xs={12}>
                    <Typography variant="h5">Recommendations</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    {
                      (this.state.booksByCollaborativeFiltering?.length || this.state.booksByPopularity?.length) ?
                        <Paper>{this.showRecommendations(this.state.booksByCollaborativeFiltering)}</Paper>
                        :
                        null
                    }
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
            <Grid item xs={6} container>
              <Grid item xs={12}>
                <Paper elevation={2} style={this.mediumGridSettings}>
                  <Grid container item >
                    <Grid item xs={12}>
                      <Typography variant="h5">User Ratings</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      {
                        (this.state.currentUserRatings?.length) ?
                          <Paper>{this.showCurrentUserRatings()}</Paper>
                          :
                          null
                      }
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
              <Grid item xs={12}>
                <Paper elevation={2} style={this.mediumGridSettings}>
                  <Grid container item spacing={1}>
                    <Grid item xs={12}>
                      <Typography variant="h5">Evaluation</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      {
                        (this.state.evaluation && Object.keys(this.state.evaluation)) ?
                          this.getEvaluations()
                          :
                          null
                      }
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            </Grid>
          </Grid>
        </Box>
      </div>
    );
  }
}

export default App;
