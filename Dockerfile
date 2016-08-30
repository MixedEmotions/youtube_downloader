FROM	ubuntu
MAINTAINER xdebef01@stud.fit.vutbr.cz
#RUN apt-get install python3 python3-httplib2 python-six python-uritemplate python-pip
RUN		apt-get update
RUN		apt-get install -y python python-dev python-setuptools libxml2-dev libxslt1-dev zlib1g-dev python-pip
RUN		pip install --upgrade pip
RUN		pip install oauth2client
RUN		pip install --upgrade google-api-python-client
RUN 	mkdir /youtube_dl
WORKDIR /youtube_dl
RUN		pip install --upgrade youtube_dl
WORKDIR cd ..
COPY . /
CMD ["python", "/youtube_downloader.py"]