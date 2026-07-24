FROM python:3.13-slim

WORKDIR /blog-maker/app
# Copy the required things
COPY ../app .

WORKDIR /blog-maker/website
COPY ../website .

# Change the directory to app
WORKDIR /blog-maker/app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py", "--host=0.0.0.0"]
