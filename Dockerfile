FROM python:3
ENV PYTHONUNBUFFERED=1
ENV USE_DOCKER=true
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
