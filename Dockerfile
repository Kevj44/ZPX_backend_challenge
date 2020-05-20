FROM python:3.7

RUN mkdir /ZPX_backend_challenge
WORKDIR /ZPX_backend_challenge
ADD . /ZPX_backend_challenge/
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "ZPX_backend_challenge.py"]