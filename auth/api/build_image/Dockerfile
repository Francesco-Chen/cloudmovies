FROM python:3.7
COPY . /app
ENV FLASK_APP=app
ENV FLASK_ENV=development
RUN pip install -r /app/requirements.txt
CMD ["flask","run","--host=0.0.0.0"]
EXPOSE 5000
