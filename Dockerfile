FROM python:3.10.1

ADD . /app
WORKDIR /app

RUN apt-get update && apt-get upgrade -y
RUN apt-get install curl -y

RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8

RUN apt-get update \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y \
    unixodbc \
    msodbcsql18 \
    ffmpeg \
    libgl1 && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip && pip install --no-cache-dir --default-timeout=100 --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5050"]