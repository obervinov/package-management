FROM almalinux:9.1

### Labels ###
LABEL org.opencontainers.image.source https://github.com/obervinov/package-management

### Environment variables ###
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_COLLATE=C
ENV LC_CTYPE=en_US.UTF-8

### Installing packages and preparing environment ###
RUN yum update -y && \
    yum install -y git \
        python3-pip \
        glibc-langpack-en && \
    yum clean all && \
    mkdir -p /opt/python

### Switching context and copying sources ###
WORKDIR /opt/python
COPY src/ ./
COPY requirements.txt ./

### Installing a python dependeces by requirements.txt and fixing a locale ###
RUN pip3 install -r requirements.txt

CMD [ "python3", "_main_.py" ]
