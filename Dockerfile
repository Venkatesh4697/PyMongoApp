FROM python:3.11.0a6-alpine3.15

WORKDIR /MongoDemo

RUN pip install Flask-PyMongo Flask-Cors

COPY . /MongoDemo

CMD python app.py --host=5001