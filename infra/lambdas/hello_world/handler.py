"""Hello-world Lambda — verification of the deploy loop.

Candidate can remove, keep as reference, or extend.
"""
import json


def handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"hello": "world", "received": event}),
    }
