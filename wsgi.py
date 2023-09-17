import flask
import json
import keybert
import logging
import uuid

kw_model = keybert.KeyBERT()

log = logging.getLogger('werkzeug')
log.disabled = True

app = flask.Flask(__name__)
logger = app.logger
logger.setLevel(logging.INFO)


def log_info(log_msg, log_data):
    logger.info(f'{log_msg} ---JSONLOG--- {json.dumps(log_data)}')


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.lineno = str(record.lineno)
        record.namespace = record.name  # record.name is the logger name
        return True


formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03dZ [%(namespace)s:%(lineno)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

f = ContextFilter()

for handler in logger.handlers:
    handler.setFormatter(formatter)
    handler.addFilter(f)


@app.before_request
def log_request_info():
    call_id = str(uuid.uuid4())
    flask.g.call_id = call_id  # store call_id in global object flask.g to access it later in response
    log_info('HTTP request', request_info(call_id, flask.request))


@app.after_request
def log_response_info(response):
    log_info(
        'HTTP response',
        response_info(
            flask.g.call_id,
            (response.get_data(as_text=True), response.status_code)
        )
    )
    return response


def request_info(call_id, request):
    return {
        "call-id": call_id,
        "protocol": request.environ.get('SERVER_PROTOCOL'),
        "remote-addr": request.remote_addr,
        "server-port": request.environ.get('SERVER_PORT'),
        "content-length": request.content_length,
        "content-type": request.content_type,
        "uri": request.path,
        "server-name": request.host,
        "body": request.get_json(force=True, silent=True),
        "scheme": request.scheme,
        "request-method": request.method,
        "args": request.args.to_dict(),
        "form": request.form.to_dict()
    }


def response_info(call_id, response):
    return {
        "status": response[1],
        "body": response[0],
        "event": "response-to-give",
        "call-id": call_id
    }


@app.route('/keywords', methods=['POST'])
def keywords():
    return kw_model.extract_keywords(
        flask.request.json['text'],
        keyphrase_ngram_range=(1, 1),
        top_n=999
    ), 200
