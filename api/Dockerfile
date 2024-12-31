FROM python:3.12-alpine3.19

# Install pipx and poetry
ENV SHELL=sh
ENV PATH="$PATH:/root/.local/bin"
RUN apk add 'pipx=~1.4'
RUN pipx install poetry==1.8.5

WORKDIR /api/
COPY . /api/
RUN poetry install

CMD ["poetry", "run", "flask", "--app", "api", "run", "--host=0.0.0.0"]
