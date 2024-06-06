FROM python

WORKDIR /app

COPY temp.py ./
COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python3", "temp.py"]