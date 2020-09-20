FROM python:3.8.2-alpine
RUN apk add --update --no-cache gcc g++
ADD requirements.txt .
RUN pip install -r requirements.txt
WORKDIR code/
ADD src/. /code
CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:app"]
EXPOSE 80
