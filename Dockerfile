FROM python:2.7
RUN mkdir -p /opt/popsapi
RUN mkdir -p /opt/popsapi/log
WORKDIR /opt/popsapi
ADD requirements.txt /opt/popsapi/
RUN pip install -r /opt/popsapi/requirements.txt

EXPOSE 80
CMD ["python", "app.py"]