# ---------- runtime stage ----------------------------------------------
FROM python:3.11

WORKDIR /srv
COPY my-languages.so /srv/my-languages.so
COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt
COPY app.py .

ENV TS_LIB=/srv/my-languages.so
EXPOSE 9000
CMD ["python", "app.py"]
