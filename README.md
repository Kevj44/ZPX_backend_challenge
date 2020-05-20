# ZPX Backend Challenge

These are instructions to run and test the REST API on a Docker container and a Kubernetes Cluster. It was built with Docker CE **v19.03** and Kubernetes **v1.18**.


## Deploy and run on a Docker container

`cd ZPX_backend_challenge`

`docker build -f Dockerfile -t zpx_backend_challenge:latest .`

`docker run -p 5000:5000 zpx_backend_challenge`

## Deploy and run on a Kubernetes cluster

First, make sure that a Kubernetes instance is running on the computer. Then run:

`cd k8s`

`kubectl create -f zpx_backend_challenge-deployment.yml` to deploy the application.

`kubectl create -f zpx_backend_challenge-service.yml` to deploy the service.

`kubectl port-forward service/zpx-backend-challenge 5000:5000` to create the port forward and access the API endpoints as shown in the previous section.

## Testing

To test the endpoints, i.e. with curl or Postman, send GET requests to:

`http://127.0.0.1:5000/ZPXsteamdata/api/v1.0/reviews` with optional parameters **page**, **per_page** or **start_date** and **end_date**.

`http://127.0.0.1:5000/ZPXsteamdata/api/v1.0/reports/votes` without any parameters.

`http://127.0.0.1:5000/ZPXsteamdata/api/v1.0/reports/reviews` with parameters **start_date** (required), **end_date** (required) and **timespan** (optional).

A Python script, multithreading_test.py, is also available in folder *ZPX_backend_challenge/tests*. It can be started once the application is already running and accepting requests. The script simulates multiple users accessing the REST API at the same time, with the JSON responses being saved in folder *ZPX_backend_challenge/tests/multithreading_test_results*. Responses contain the query parameters (if any), the time it took the query to run as well as the JSON results.
