import axios from 'axios';

const bookRecommenderApi = axios.create({
    baseURL: "http://localhost:5000",
    headers: {
        'Content-Type': 'application/json'
    },
    validateStatus: (status) => { return status === 200; }
});

export const getSimilarity = async () => {
    return bookRecommenderApi.get("getSimilarity")
};