FROM keitarodxs/aia:aia-utils_0.1.6
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry
COPY . .
COPY pyproject.toml poetry.lock ./
RUN poetry install

CMD [ "poetry", "run", "daemon"]
