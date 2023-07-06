FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
	dos2unix \
	iputils-ping \
	nano \
	tzdata\
	procps\
	ffmpeg\
	flac

# create the app user
RUN addgroup --system app && adduser --system --group app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# test/debug mode
# ENTRYPOINT ["tail", "-f", "/dev/null"]

CMD [ "python", "main.py" ]