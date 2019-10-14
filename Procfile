web: gunicorn -w 4 -b "0.0.0.0:$PORT" app:app
heroku ps:scale web=1
worker: python3 discord-bot.py