FROM ubuntu:16.10 

RUN apt-get -y update

RUN apt-get install -y curl


#Upgrade pip
RUN apt-get install -y python-dev python-pip
RUN pip install --upgrade pip

RUN apt-get install -y libmysqlclient-dev

RUN pip install mysql-python

RUN mkdir /exchange
ADD exchange.py /exchange/exchange.py
ADD main.py /exchange/main.py

ENTRYPOINT python /exchange/main.py