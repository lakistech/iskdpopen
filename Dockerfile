FROM python

RUN mkdir /iskdpoen
ADD . /iskdpopen
WORKDIR /iskdpopen
RUN pip3 install -r requirements.txt
ENV PYTHONUNBUFFERED 1
CMD uvicorn app:app --host 0.0.0.0
