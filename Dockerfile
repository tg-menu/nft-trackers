FROM python:3.11

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --verbose -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
