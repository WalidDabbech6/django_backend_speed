FROM python:3.9

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /app

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app/

RUN apt-get update && apt-get install -y locales locales-all

RUN update-locale LANG=fr_FR.UTF-8

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt