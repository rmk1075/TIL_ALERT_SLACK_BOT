# Build an Image starting with the Python 3.7 image
FROM ubuntu:18.04

# LABEL for author
LABEL author="jamie"
LABEL email="rmk1075@gmail.com"

# install python3
RUN apt-get update -y
RUN apt-get install -y python3 python3-pip python3-dev build-essential
RUN apt-get install git -y

# set the working directory to /usr/app in docker container
WORKDIR /usr/app

# copy the current directory . in project to the workdir . in the image
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
