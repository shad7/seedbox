FROM alpine:3.1

RUN apk add --update py-pip python \
    && rm -rf /var/cache/apk/* \
    && ln -s /usr/etc/seedbox /etc/seedbox

COPY . /seedbox/

WORKDIR /seedbox

RUN apk add --update git g++ python-dev \
    && pip install -U -r /seedbox/requirements.txt \
    && python setup.py install \
    && apk del git g++ python-dev \
    && rm -rf /var/cache/apk/* \
    && rm -rf .git/ \
    && rm -rf build/

VOLUME ["/usr/etc/seedbox"]
EXPOSE 5000

CMD ["seedmgr"]

