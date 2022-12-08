FROM python:3.7.3

ADD stop_order_update.py .

RUN pip3 install flask

RUN pip3 install requests

RUN pip3 install nano

CMD ["python", "./stop_order_update.py"]
