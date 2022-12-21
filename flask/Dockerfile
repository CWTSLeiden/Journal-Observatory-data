# Base docker image, Python version
FROM python:3.11-alpine

# Install requirements
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Copy application
COPY ./src/api /app/src/api
COPY ./src/utils /app/src/utils
COPY ./resources /app/resources
COPY ./flask/start.sh /docker-entrypoint.sh

# Start application
ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]
CMD ["run"]
