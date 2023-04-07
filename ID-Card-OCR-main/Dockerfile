# using ubuntu LTS version
#FROM ubuntu:20.04
FROM python:3.9

# author
MAINTAINER Muhammad Ahmad

# extra metadata
LABEL version = "1.0"
LABEL description="OCR Product Suite API with Dockerfile."

# avoid stuck build due to user prompt
#ARG DEBIAN_FRONTEND=noninteractive

#RUN apt-get --no-install-recommends update && \
#	apt-get install --no-install-recommends -y python3.9 python3.9-dev python3-pip python3-wheel build-essential python3-opencv gunicorn && \
#	apt-get clean && rm -rf /var/lib/apt/lists/*

#ADD OCR-ubuntu-debs OCR-ubuntu-debs
#RUN dpkg -i OCR-ubuntu-debs/*
#RUN rm -rf OCR-ubuntu-debs
#RUN apt-get install -qy ffmpeg libsm6 libxext6

# install requirements
COPY requirements.txt .
COPY /static/img/Hbl.PNG .
#RUN pip3 install Pillow
#RUN pip3 install opencv-python
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt

RUN easyocr -l en -f Hbl.PNG

RUN rm -rf requirements.txt Hbl.PNG

#RUN useradd --create-home ocr-user

#USER myuser
RUN mkdir /home/code
WORKDIR /home/code
#COPY . .

EXPOSE 5000

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

# CMD ["gunicorn","-b", "0.0.0.0:5000", "-w", "4", "--timeout", "600", "--worker-tmp-dir", "/dev/shm", "app:app"]
CMD ["gunicorn","-c", "configuration.ini", "--worker-tmp-dir", "/dev/shm", "app:app"]