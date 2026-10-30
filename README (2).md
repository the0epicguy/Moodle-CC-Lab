# CC Lab Assignment 4: Docker and Kubernetes

## Application
A Node.js HTTP server that displays the hostname of the container serving the request.

## Requirements
- Docker Desktop using Linux containers
- kubectl
- Minikube

## Build the Docker image
docker build -t cc-k8s-demo:v1 .

## Make the image available to Minikube
minikube image load cc-k8s-demo:v1

## Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

## Verify
kubectl get nodes
kubectl get deployments
kubectl get pods -o wide
kubectl get services

## Open the service
minikube service cc-demo-service --url

Open the URL printed by Minikube in your browser.

## Demonstrate scaling
kubectl scale deployment/cc-demo --replicas=5
kubectl get pods -w

Press Ctrl+C to stop watching.

## Demonstrate self-healing
kubectl get pods
kubectl delete pod <one-of-the-cc-demo-pod-names>
kubectl get pods -w

Kubernetes should create a replacement Pod to maintain the desired replica count.

## Optional automatic scaling
kubectl apply -f k8s/hpa.yaml
kubectl get hpa -w

The Horizontal Pod Autoscaler requires the metrics API. If CPU metrics are unavailable, enable Minikube's metrics-server addon:
minikube addons enable metrics-server

## Clean up
kubectl delete -f k8s/hpa.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
