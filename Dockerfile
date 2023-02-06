ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}
ENV PYTHONUNBUFFERED=1
ENV USE_DOCKER=true
WORKDIR /code
COPY . /code/
RUN echo "Use legency resolver for pip. It does not use the feature back-tracking. Thus is easier to debug imcompatible dependencies."
RUN pip install --upgrade pip --use-deprecated=legacy-resolver
ARG DJANGO_VERSION="3.1.7"
RUN echo "Installing Django Version: ${DJANGO_VERSION}"
RUN pip install django==${DJANGO_VERSION}
RUN pip install -r requirements.txt
RUN pip install -e .
ARG SELENIUM_VERSION="4.0.0a7"
RUN echo "Installing Selenium Version: ${SELENIUM_VERSION}"
RUN pip install selenium~=${SELENIUM_VERSION}
