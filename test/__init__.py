import azure.functions as func
import logging
import requests


def get(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")

    if name:
        return func.HttpResponse(
            f"Hello, {name}. This HTTP triggered function executed successfully."
        )
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200,
        )


def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info("timer: Python HTTP trigger function processed a request.")

    # parse method type
    logging.info("timer: method={}".format(req.method))
    if req.method == "GET":
        return get(req)
    else:
        return func.HttpResponse(status_code=405)
