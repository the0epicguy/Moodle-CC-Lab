# Cloud Computing Lab Assignment 4: Docker and Kubernetes

## 1. Aim

To containerise a web application using Docker, deploy it on Kubernetes using Minikube, and demonstrate scaling and self-healing.

## 2. Tools Used

- Docker Desktop
- Minikube
- Kubernetes
- `kubectl`
- Node.js
- Windows PowerShell

## 3. Project Structure

The project should contain the application code, Docker configuration, and Kubernetes manifest files.

```text
project-folder/
├── app.js
├── package.json
├── Dockerfile
├── .dockerignore
├── README.md
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    └── hpa.yaml
```

### Purpose of the Files

- `app.js`: Runs the web application and displays the hostname of the container serving the request.
- `package.json`: Defines the Node.js application and its start command.
- `Dockerfile`: Specifies how to build the Docker image.
- `.dockerignore`: Excludes unnecessary files from the Docker build context.
- `k8s/deployment.yaml`: Defines the Deployment, replica count, resource limits, and health probes.
- `k8s/service.yaml`: Exposes the application using a NodePort Service.
- `k8s/hpa.yaml`: Defines an optional Horizontal Pod Autoscaler.
- `README.md`: Contains project information and instructions.

## 4. Check the Installed Tools

Run the following commands in PowerShell:

```powershell
docker --version
docker info
kubectl version --client
minikube version
```

Docker Desktop must be running before starting Minikube with the Docker driver.

## 5. Start Minikube

Start the Kubernetes cluster:

```powershell
minikube start --driver=docker
```

Set the current Kubernetes context:

```powershell
kubectl config use-context minikube
```

Verify that the node is ready:

```powershell
kubectl get nodes
```

The Minikube node should show the status `Ready`.

## 6. Build the Docker Image

Run the following command from the project directory:

```powershell
docker build -t cc-k8s-demo:v1 .
```

Explanation:

- `docker build` builds the image.
- `-t cc-k8s-demo:v1` assigns the image name and version.
- `.` uses the current directory as the build context.

Verify that the image exists:

```powershell
docker images cc-k8s-demo
```

## 7. Load the Image into Minikube

Load the locally built image into the Minikube cluster:

```powershell
minikube image load cc-k8s-demo:v1
```

This allows Kubernetes to use the image without downloading it from a remote registry.

## 8. Deploy the Application

Apply the Kubernetes Deployment configuration:

```powershell
kubectl apply -f .\k8s\deployment.yaml
```

Wait for the Deployment to become ready:

```powershell
kubectl rollout status deployment/cc-demo --timeout=180s
```

Check the Deployment and Pods:

```powershell
kubectl get deployment cc-demo
kubectl get pods -l app=cc-demo
```

The initial Deployment is configured for three replicas.

## 9. Create the Kubernetes Service

Apply the Service configuration:

```powershell
kubectl apply -f .\k8s\service.yaml
```

Inspect the Service:

```powershell
kubectl get services
kubectl describe service cc-demo-service
```

The Service exposes port 80 and forwards traffic to container port 3000 through a NodePort.

## 10. Open the Web Application

Run:

```powershell
minikube service cc-demo-service --url
```

Open the URL printed by Minikube in your browser. The URL and port may change between sessions.

Keep the terminal running while accessing the website because the local forwarding process may depend on that terminal remaining open.

The application displays the hostname of the container handling the request, demonstrating that the application is running inside Kubernetes.

## 11. Demonstrate Scaling

Initially, the Deployment uses three replicas. Increase the replica count to five:

```powershell
kubectl scale deployment cc-demo --replicas=5
```

Wait for all replicas to become ready:

```powershell
kubectl rollout status deployment/cc-demo --timeout=180s
```

Verify the Deployment:

```powershell
kubectl get deployment cc-demo
```

List the Pods:

```powershell
kubectl get pods -l app=cc-demo -o wide
```

Expected result:

- Five Pods should be running.
- The Deployment should show `5/5` ready replicas.

This demonstrates **scaling**. Kubernetes creates additional Pods to match the desired replica count.

## 12. Demonstrate Self-Healing

First, list the Pods:

```powershell
kubectl get pods -l app=cc-demo
```

Choose one of the actual Pod names displayed. Delete that Pod using its current name:

```powershell
kubectl delete pod <actual-pod-name>
```

Replace `<actual-pod-name>` with the name of a real Pod. Do not type the angle brackets.

To observe the Pods changing in real time, open another PowerShell terminal and run:

```powershell
kubectl get pods -l app=cc-demo -w
```

Kubernetes should create a replacement Pod after the original Pod is deleted.

Press `Ctrl+C` to stop watching. Verify the final state:

```powershell
kubectl get deployment cc-demo
kubectl get pods -l app=cc-demo
```

Expected result: the Deployment returns to five ready replicas.

This demonstrates **self-healing**. The Kubernetes Deployment controller maintains the desired replica count by creating replacement Pods when necessary.

## 13. Verify Service Endpoints

Inspect the Service:

```powershell
kubectl describe service cc-demo-service
```

Inspect its EndpointSlices:

```powershell
kubectl get endpointslices -l kubernetes.io/service-name=cc-demo-service -o wide
```

The output should show the addresses of the Pods selected by the Service. This confirms that the Service has multiple backend Pods available.

## 14. Optional Application Logs

View recent logs:

```powershell
kubectl logs deployment/cc-demo --tail=20
```

The output depends on what the application logs while handling requests.

## 15. Screenshots to Capture for the Practical

### Screenshot 1: Website in the Browser

Show the application displaying the hostname of the container.

### Screenshot 2: Docker Image and Kubernetes Node

```powershell
docker images cc-k8s-demo
kubectl get nodes
```

### Screenshot 3: Five Running Pods

```powershell
kubectl get deployment cc-demo
kubectl get pods -l app=cc-demo -o wide
```

### Screenshot 4: Self-Healing

Delete a Pod and watch the replacement:

```powershell
kubectl get pods -l app=cc-demo -w
```

In another terminal:

```powershell
kubectl delete pod <actual-pod-name>
```

Verify the final state:

```powershell
kubectl get deployment cc-demo
kubectl get pods -l app=cc-demo
```

### Screenshot 5: Service and Endpoints

```powershell
kubectl get services
kubectl describe service cc-demo-service
kubectl get endpointslices -l kubernetes.io/service-name=cc-demo-service -o wide
```

Use `Win + Shift + S` to capture screenshots on Windows.

## 16. Stop the Application Safely

Stop the local forwarding process by pressing `Ctrl+C` in the terminal running the Minikube Service URL command.

Scale the application to zero replicas:

```powershell
kubectl scale deployment cc-demo --replicas=0
```

Verify:

```powershell
kubectl get pods -l app=cc-demo
```

Stop Minikube:

```powershell
minikube stop
```

Docker Desktop can be left running or quit after Minikube stops.

Do not run `minikube delete` or `docker system prune` just to stop the practical. These commands are unnecessary for normal shutdown.

## 17. Start the Practical Again

Start Docker Desktop and open PowerShell. Navigate to the project directory using the location where the project was saved. Then start Minikube:

```powershell
minikube start --driver=docker
kubectl config use-context minikube
kubectl get nodes
```

Restore five replicas:

```powershell
kubectl scale deployment cc-demo --replicas=5
kubectl rollout status deployment/cc-demo --timeout=180s
```

Open the application:

```powershell
minikube service cc-demo-service --url
```

Keep the terminal open while accessing the website.

If the Kubernetes resources were deleted, recreate them from the project directory:

```powershell
docker build -t cc-k8s-demo:v1 .
minikube image load cc-k8s-demo:v1
kubectl apply -f .\k8s\deployment.yaml
kubectl apply -f .\k8s\service.yaml
kubectl rollout status deployment/cc-demo --timeout=180s
minikube service cc-demo-service --url
```

## 18. Troubleshooting

### Wrong Kubernetes Context

```powershell
kubectl config use-context minikube
kubectl get nodes
```

### Pods Are Not Starting

```powershell
kubectl get pods -l app=cc-demo
kubectl describe pods -l app=cc-demo
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Local Image Is Unavailable to Kubernetes

```powershell
minikube image load cc-k8s-demo:v1
```

Restart the Deployment if needed:

```powershell
kubectl rollout restart deployment/cc-demo
kubectl rollout status deployment/cc-demo --timeout=180s
```

### Website URL No Longer Works

Run the Service URL command again:

```powershell
minikube service cc-demo-service --url
```

Open the newly printed URL and keep its terminal open.

### Deployment Has Fewer Than Five Replicas

```powershell
kubectl scale deployment cc-demo --replicas=5
kubectl rollout status deployment/cc-demo --timeout=180s
kubectl get deployment cc-demo
kubectl get pods -l app=cc-demo
```

## 19. Conclusion

A Node.js web application was containerised using Docker and deployed to Kubernetes using Minikube. A Kubernetes Deployment managed the application replicas, while a NodePort Service provided access to the application. The Deployment was scaled from three replicas to five, demonstrating scaling. Deleting a Pod and observing Kubernetes create a replacement demonstrated self-healing.

The practical covered Docker image creation, Kubernetes deployment, Service exposure, scaling, endpoint verification, and automatic recovery from Pod deletion.
