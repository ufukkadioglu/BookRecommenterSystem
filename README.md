## Hybrid Book Recommender System Using Collaborative Filtering and Popularity-Based Recommendations

This is a simple school project implemented for Recommender Systems course on Computer Engineering Master’s Degree
program. It simply recommends books for the users who already have some ratings in the dataset using Collaborative
Filtering. For the users who do not have any ratings yet, the system uses Popularity-Based recommendations to prevent
user based cold start.

Dataset: Book-Crossing

Data source: http://www2.informatik.uni-freiburg.de/~cziegler/BX/

For Collaborative Filtering:
https://medium.com/grabngoinfo/recommendation-system-user-based-collaborative-filtering-a2e76e3e15c4

For Popularity-Based Recommendations:
https://stackoverflow.com/questions/54357300/bayesian-averaging-in-a-dataframe

Project repository:
https://github.com/ufukkadioglu/BookRecommenterSystem

### Running the project:

If you use docker and docker compose you can start project running below compose command on project root (where the 
docker-compose.yaml is located):

docker compose up --wait --detach --build

The command will start 2 containers; book_recommender_api listening port 5000 and book_recommender_ui listening port
5001, if these ports are not available on your machine you should update docker compose file for available ports.

You can also run the project without docker, but it would require more effort:
1. Create python virtual environment for the api
2. Install python requirements
3. Run app.py on api directory
4. Switch to user interface and install node packages using npm install
5. Start user interface using npm start

Note that backend will still work on port 5000 but the frontend starts on port 3000 when you directly run npm start, 
frontend port mapping is made on docker compose file, so that npm will not know the custom port when you run manually.

### General project structure:

![project_structure.png](images%2Fproject_structure.png)

### How does it work:

![project_flow.png](images%2Fproject_flow.png)

Collaborative recommendations:

![collaborative_rocommendations.png](images%2Fcollaborative_rocommendations.png)

Popularity-Based Recommendations:

![popularity_based_recommendations.png](images%2Fpopularity_based_recommendations.png)