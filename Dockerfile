FROM alpine:3.11
ENV PYTHON_VERSION 3.7.4
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN apk --update add python3 py-pip openssl ca-certificates py-openssl wget bash linux-headers
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install --upgrade pipenv\
  && pip install --upgrade -r /app/requirements.txt\
  && apk del build-dependencies

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "hello.py" ]