FROM python:3.15.0a1-alpine3.22

RUN apk add --no-cache libxslt-dev
RUN apk add --no-cache gcc
RUN apk add --no-cache libxml2
RUN apk add --no-cache g++

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY docker_config.json ./config.json
COPY src/ ./

CMD [ "python", "./generate_dictionary.py" ]
