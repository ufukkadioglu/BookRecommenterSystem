import axios from 'axios';

const bookRecommenderApi = axios.create({
    baseURL: "http://localhost:5000",
    headers: {
        'Content-Type': 'application/json'
    },
    validateStatus: (status) => { return status === 200; }
});

export const getUsers = async () => {
    return bookRecommenderApi.get("getUsers")
};

export const getRecommendedBooks = async (userId) => {
    return bookRecommenderApi.get("getRecommendedBooks", { params: { user_id: userId } })
};