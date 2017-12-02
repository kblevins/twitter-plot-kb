# twitter-plot-kb
A twitter bot for sentiment analysis. The twitter screen name for the bot is '@plot_kb'. If you tweet a message at this bot containing a twitter screen name it will return a plot with the sentiment scores from that user's last 500 tweets. 

Contents of this repo:

* main.py - contains main program for running the bot

* Procfile - file specifying that main.py is the worker file for a Heroku app

* requirements - file containing a list of the modules that need to be pip installed for the Heroku app

* testing.ipynb - Jupyter notebook for testing pieces of the main.py code

  ​

This bot uses the following python packages:

* Matplotlib
* Seaborn
* VADER sentiment analysis