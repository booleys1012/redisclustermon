FROM python:2.7

COPY dist                   /app/dist
COPY client/dist            /app/static
COPY client/dist/assets/.  /app/static

RUN pip install /app/dist/redisclustermon-0.0.20180423.1.tar.gz

CMD [ "rcm.py" ]
