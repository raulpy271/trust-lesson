FROM python:3.12-alpine3.19

WORKDIR /api/
COPY requirements.txt /api/requirements.txt
RUN pip install -r /api/requirements.txt
COPY . /api/

CMD ["flask", "--app", "api", "run", "--host=0.0.0.0"]
