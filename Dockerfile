# syntax=docker/dockerfile:1

FROM ubuntu
MAINTAINER Mengru Ji

RUN apt-get update -y

RUN apt-get update && apt-get install -y python3.9 python3-distutils python3-pip python3-apt

RUN apt-get install -y git

RUN git clone https://github.com/carrieMrJ/Group4-Automatic-Conformance-Checking-insights-in-Celonis
WORKDIR /Group4-Automatic-Conformance-Checking-insights-in-Celonis
RUN pip install --extra-index-url=https://pypi.celonis.cloud/ pycelonis=="2.3.0"
# RUN pip freeze > requirements.txt
RUN pip install flask
RUN pip install numpy
RUN pip install pandas
RUN pip install PyYAML
RUN pip install matplotlib
RUN pip install scikit-learn
#RUN pip install -r requirements.txt

COPY . /Group4-Automatic-Conformance-Checking-insights-in-Celonis

EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["app.py"]
