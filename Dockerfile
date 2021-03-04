FROM python:3.8
ENV PYTHONUNBUFFERED=1
ENV USE_DOCKER=true
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt
RUN pip install -e .
