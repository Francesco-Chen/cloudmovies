FROM python:3.7-alpine
COPY . /app
ENV FLASK_APP=/app/favorites_app.py
ENV FLASK_ENV=development
RUN pip install -r /app/requirements.txt
CMD ["flask","run","--host=0.0.0.0","--port=5003"]
EXPOSE 5003
