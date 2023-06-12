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
    recommendedBooks: [],
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
          recommendedBooks: response.data.books_to_recommend,
          selectedUser: selectedUser
        })
      }).catch(err => console.log(err));
    }
  }

  getRecommendations() {
    return (
      <>
      <TableContainer component={Paper}>
        <Table size="small" aria-label="a dense table">
          <TableHead>
            <TableRow>
              <TableCell>Order</TableCell>
              <TableCell>ISBN</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Author</TableCell>
              <TableCell>Year</TableCell>
              <TableCell>Predicted Score (Normalized)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {this.state.recommendedBooks?.map((book, idx) => (
              <TableRow
                key={book.isbn}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                <TableCell component="th" scope="row">{idx + 1}</TableCell>
                <TableCell>{book.isbn}</TableCell>
                <TableCell>{book.bookTitle}</TableCell>
                <TableCell>{book.author}</TableCell>
                <TableCell>{book.yearOfPublication}</TableCell>
                <TableCell>{book.scorePrediction.toFixed(3)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      </>
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

            <Grid item xs={6}>
              {
                this.state.recommendedBooks?.length ?
                  <Paper>{this.getRecommendations()}</Paper>
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
