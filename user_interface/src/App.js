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

class App extends React.Component {
  state = {
    selectedUser: "",
    booksByCollaborativeFiltering: [],
    booksByPopularity: [],
    userIds: [],
  }

  componentDidMount() {
    getUsers().then(response => {
      this.setState({
        userIds: response.data.user_ids,
      });
    }).catch(err => console.log(err));
  }

  getUserSelector() {
    return (
      <FormControl fullWidth>
        <InputLabel id="demo-simple-select-label">User Id</InputLabel>
        <Select
          labelId="demo-simple-select-label"
          id="demo-simple-select"
          value={this.state.selectedUser}
          label="Age"
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
      getRecommendedBooks(selectedUser).then(response => {
        this.setState({
          booksByCollaborativeFiltering: response.data.collaborative_filtering,
          booksByPopularity: response.data.popularity_based,
          selectedUser: selectedUser
        })
      }, () => console.log(this.state.booksByPopularity)).catch(err => console.log(err));
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

  render() {
    return (
      <div className="App" >
        <Box sx={{ flexGrow: 1 }}>
          <Grid container spacing={2}>
            <Grid item xs={2}>
              <Paper>{this.getUserSelector()}</Paper>
            </Grid>
            <Grid item xs={10}>
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
        </Box>
      </div>
    );
  }
}

export default App;
