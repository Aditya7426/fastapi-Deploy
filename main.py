from fastapi import FastAPI, HTTPException
from kubernetes import client, config
import subprocess

app = FastAPI()

# Load Kubernetes configuration
config.load_kube_config()

@app.post("/createDeployment/{deployment_name}")
async def create_deployment(deployment_name: str):
    try:
        # Define deployment spec
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=deployment_name),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector={"matchLabels": {"app": deployment_name}},
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": deployment_name}),
                    spec=client.V1PodSpec(containers=[
                        client.V1Container(
                            name=deployment_name,
                            image="nginx:latest",  # You can change this to any other image
                            ports=[client.V1ContainerPort(container_port=80)]
                        )
                    ])
                )
            )
        )

        # Create deployment
        api_instance = client.AppsV1Api()
        api_instance.create_namespaced_deployment(
            namespace="default",
            body=deployment
        )
        return {"message": f"Deployment {deployment_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/getPromdetails")
async def get_prom_details():
    try:
        # Get all pods in the default namespace
        api_instance = client.CoreV1Api()
        pods = api_instance.list_namespaced_pod(namespace="default")
        pod_details = [{"name": pod.metadata.name, "status": pod.status.phase} for pod in pods.items]
        return {"pods": pod_details}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    subprocess.run(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])
