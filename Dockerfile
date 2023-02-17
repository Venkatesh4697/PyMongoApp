FROM python:3.11.0a6-alpine3.15

RUN apk update
RUN apk add git
RUN git clone https://github.com/Venkatesh4697/PyMongoApp.git
WORKDIR /PyMongoApp

RUN pip install Flask-PyMongo Flask-Cors PyJWt

COPY . /PyMongoApp

CMD python app.py 
