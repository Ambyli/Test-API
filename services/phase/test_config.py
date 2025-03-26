import azure.functions as func
import os
import json


class main:
    def HttpRequest(method, url, body=None, params=None):
        token = str(os.getenv("OWNER_DEFAULT_TOKEN"))

        headers = {"Token": token}
        if method in ["GET", "DELETE"]:
            if params == None:
                params = {}
            if "employeeIDs" not in params:
                params["employeeIDs"] = os.getenv("OWNER_DEFAULT_EMPLOYEE_ID")
        else:
            # Check if body is a dictionary and has a certain key
            if isinstance(body, bytes):
                # Decode the body from bytes to a string
                body_str = body.decode("utf-8")
                try:
                    # Parse the string as JSON
                    body_dict = json.loads(body_str)
                    if "employeeIDs" not in body_dict:
                        # Add default key-value pair to the body
                        body_dict["employeeIDs"] = [
                            os.getenv("OWNER_DEFAULT_EMPLOYEE_ID")
                        ]
                    # Encode the modified dictionary back to bytes
                    body = json.dumps(body_dict).encode("utf-8")
                except json.JSONDecodeError:
                    # If the body is not valid JSON, handle the error as needed
                    pass
            elif isinstance(body, dict) and "employeeIDs" not in body:
                # Add default key-value pair to the body
                body["employeeIDs"] = [os.getenv("OWNER_DEFAULT_EMPLOYEE_ID")]

        return func.HttpRequest(
            method=method, url=url, body=body, params=params, headers=headers
        )
