# swap-image

TBD

## Installation of the Mutating Webhook

### Build the Image

Review the makefile and perhaps Dockerfile and run:

```
make image
```

### Deployment

Now that the certificate infrastructure is sorted, we can deploy the webhook.

* Create a namespace for the webhook

```
k create -f manifests/namespace.yaml
```

* Create a certificate for the webhook

```
k create -f manifests/certs.yaml
```

* Create the Mutating webhook configuration

```
k create -f manifests/mutating-webhook-configuration.yaml
```

* Deploy the webhook

```
k create -f manifests/deployment.yaml
k create -f manifests/service.yaml
```

## Testing

TBD
