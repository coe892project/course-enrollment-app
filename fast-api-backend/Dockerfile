FROM python:3.13

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./main.py /code/
COPY ./DummyData /code/DummyData/

EXPOSE 80

CMD ["fastapi", "run", "main.py", "--port", "80"]
