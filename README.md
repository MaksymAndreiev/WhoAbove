# Who above?

This project has entertainment purposes only. This is a simple
web application to predict the outcome of a popular Ukrainian TV show "Who Above?".
The show is a competition between two teams of celebrities who compete in various games. Teams are divided by gender and
the goal of the show is to determine who is better: men or women (not really, it's just a show).
The application is based on the results of the previous seasons of the show.

The user can select the participants of each team: male team and female team;
and the application will predict the team that will win.
The application is designed to be used by the fans of the show who want to have fun.

## How to install

To use this app, you can easily access it through Docker:

````
docker pull maksymandreiev17/who_above
````

Then run the image:

````
docker run -it --rm -p 8080:5000 maksymandreiev17/who_above
````

or you can use other port instead of 8080.

After that, you can access the app through your browser by typing `http://localhost:8080/` in the address bar.

Other way to use the app is to clone the repository and run the app locally:

````
git clone https://github.com/MaksymAndreiev/WhoAbove.git
cd WhoAbove
pip install -r requirements.txt
python main.py
````

