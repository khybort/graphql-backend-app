FROM python:3.10

RUN pip install pipenv

WORKDIR ./core

COPY Pipfile Pipfile.lock ./

RUN pipenv install

COPY . ./

EXPOSE 8000

CMD ["pipenv", "run", "uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]