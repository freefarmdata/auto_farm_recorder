from python:3.8.5

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

WORKDIR /usr/src/app/src

CMD ["python3", "main.py"]