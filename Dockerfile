ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}
ENV PYTHONUNBUFFERED=1
ENV USE_DOCKER=true
WORKDIR /code
COPY . /code/
ARG DJANGO_VERSION="3.1.7"
RUN pip install django==${DJANGO_VERSION}
RUN pip install -r requirements.txt
RUN pip install -e .
ARG SELENIUM_VERSION="4.0.0a5"
RUN pip install selenium==${SELENIUM_VERSION}
