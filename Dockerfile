FROM keitarodxs/aia:aia-utils_0.1.7
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry
COPY . .
COPY pyproject.toml poetry.lock ./
RUN rm poetry.lock
#RUN poetry add RPi.GPIO
#RUN poetry add spidev
RUN poetry install

CMD [ "poetry", "run", "daemon"]
