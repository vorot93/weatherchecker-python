FROM python:latest
ENV APP_HOME /usr/src/app
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

ADD requirements.txt $APP_HOME
RUN pip install --no-cache-dir -r requirements.txt

ADD . $APP_HOME
