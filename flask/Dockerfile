# Base docker image, Python version
FROM python:3.11-alpine

# Install requirements
COPY ../requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Copy application
COPY ../src/api /app/src/api
COPY ../src/utils /app/src/utils
COPY ../config /app/config
COPY ../data /app/data

# Start application
ENTRYPOINT [ "python" ]
CMD [ "/app/src/api/api.py" ]
