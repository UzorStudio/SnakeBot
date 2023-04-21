FROM python:3.10
WORKDIR /app
COPY telegram_interf .
RUN pip3 install --no-cache-dir -r req.txt
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
CMD ["python3.10","main.py"]
