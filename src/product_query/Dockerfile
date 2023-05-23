FROM python:latest
COPY . /app
COPY ../product_updater/product_updater.py /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD["product_query.py"]