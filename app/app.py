from flask import Flask, request, jsonify
import json
import base64
import logging
import os

app = Flask(__name__)

SWAP_IMAGE = "nginxinc/nginx-unprivileged:latest"


def create_patches(containers):
    patches = []
    for i, container in enumerate(containers):
        patches.append(
            {
                "op": "replace",
                "path": f"/spec/containers/{i}/image",
                "value": SWAP_IMAGE,
            }
        )
    return patches


@app.route("/mutate", methods=["POST"])
def mutate_pod():
    try:
        admission_review_request = request.get_json()
        if admission_review_request is None:
            raise ValueError("No JSON payload or invalid content type")

        containers = (
            admission_review_request.get("request", {})
            .get("object", {})
            .get("spec", {})
            .get("containers")
        )
        if containers is None:
            raise ValueError("Invalid request format")

        patches = create_patches(containers)
        patch_base64 = base64.b64encode(json.dumps(patches).encode()).decode()

        admission_review_response = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": admission_review_request["request"]["uid"],
                "allowed": True,
                "patchType": "JSONPatch",
                "patch": patch_base64,
            },
        }
        return jsonify(admission_review_response)

    except ValueError as val_error:
        app.logger.error(f"Request handling error: {val_error}")
        return jsonify({"error": str(val_error)}), 400
    except Exception as exc:
        app.logger.error(f"Unexpected error: {exc}")
        return jsonify({"error": "Unexpected error occurred"}), 500


if __name__ != "__MAIN__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.info("Starting swap-image webhook...")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.environ.get("FLASK_RUN_PORT", "8080"))
    app.logger.info(f"Starting app on port {port}")
    app.run(host="0.0.0.0", port=port)
