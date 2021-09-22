FROM python:3.6-buster

RUN apt-get update
RUN apt-get install -y libffi-dev libopus-dev ffmpeg

ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD pascal.py .
ADD voice.py .

CMD ["python", "-u", "pascal.py"]