FROM python:3-slim
WORKDIR /usr/src/pnlviewer
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5006
CMD bokeh serve .