FROM python:3.7-alpine
LABEL maintainer="makssych@gmail.com"
RUN mkdir -p /app/config
COPY . /app
WORKDIR /app
CMD ["/app/harborctl.py", "-h"]