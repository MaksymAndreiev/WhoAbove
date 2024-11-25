FROM python:3.9-slim

RUN pip install pipenv
RUN python3 -m pip install --upgrade pip setuptools wheel

WORKDIR /app
COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY ["main.py", "./"]
COPY ["templates", "./templates"]
COPY ["saves", "./saves"]
COPY ["requirements.txt", "./"]
COPY ["data", "./data"]

RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["waitress-serve", "--host=0.0.0.0", "--port=5000", "main:app"]