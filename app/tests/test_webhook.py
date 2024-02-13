import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))
from app import app
import unittest
import json
import base64
import logging

SWAP_IMAGE = "nginxinc/nginx-unprivileged:latest"

logging.basicConfig(level=logging.DEBUG)


class TestMutatingWebhook(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_invalid_json(self):
        response = self.app.post(
            "/mutate", data='{"invalidJson":}', content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_json())

    def test_mutate_pod(self):
        # Mock AdmissionReview request
        mock_request = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "request": {
                "uid": "some-unique-id",
                "object": {
                    "apiVersion": "v1",
                    "kind": "Pod",
                    "spec": {
                        "containers": [
                            {"name": "example-container", "image": "example-image"}
                        ]
                    },
                },
            },
        }

        # Send mock request to the webhook endpoint
        response = self.app.post("/mutate", json=mock_request)

        # Assert the response
        self.assertEqual(response.status_code, 200)
        # Additional assertions to verify the response content

        response_data = response.get_json()
        patch_base64 = response_data["response"]["patch"]
        patch = json.loads(base64.b64decode(patch_base64))

        print(patch)

        # Check if the patch contains an operation to change the image
        image_patch_found = any(
            op["op"] == "replace"
            and op["path"].endswith("/image")
            and op["value"] == SWAP_IMAGE
            for op in patch
        )

        self.assertTrue(
            image_patch_found, "Patch to change image not found in response"
        )

    def test_bad_request(self):
        # Malformed AdmissionReview request
        bad_request = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            # Deliberately malformed request
            "request": {
                "uid": "some-unique-id",
                # Missing 'object' key or other necessary data
            },
        }

        # Send malformed request to the webhook endpoint
        response = self.app.post("/mutate", json=bad_request)

        # Assert the response is an error
        self.assertEqual(response.status_code, 400)
        # Additional assertions to verify the response content
        response_data = response.get_json()
        self.assertIn("error", response_data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
