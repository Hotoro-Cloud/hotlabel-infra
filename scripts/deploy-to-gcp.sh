#!/bin/bash

# Deploy HotLabel infrastructure to GCP Compute Engine
# Usage: ./deploy-to-gcp.sh [PROJECT_ID] [INSTANCE_NAME] [ZONE]

set -e

# Default values
PROJECT_ID=${1:-"hotlabel-project"}
INSTANCE_NAME=${2:-"hotlabel-instance"}
ZONE=${3:-"us-central1-a"}
MACHINE_TYPE="e2-standard-4"

echo "Deploying HotLabel infrastructure to GCP..."
echo "Project ID: $PROJECT_ID"
echo "Instance Name: $INSTANCE_NAME"
echo "Zone: $ZONE"
echo "Machine Type: $MACHINE_TYPE"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Ensure project is set
gcloud config set project "$PROJECT_ID"

# Check if instance already exists
if gcloud compute instances describe "$INSTANCE_NAME" --zone="$ZONE" &> /dev/null; then
    echo "Instance $INSTANCE_NAME already exists."
else
    echo "Creating new Compute Engine instance..."
    
    # Create the VM instance
    gcloud compute instances create "$INSTANCE_NAME" \
        --zone="$ZONE" \
        --machine-type="$MACHINE_TYPE" \
        --image-family="debian-11" \
        --image-project="debian-cloud" \
        --boot-disk-size="50GB" \
        --tags="http-server,https-server" \
        --metadata="startup-script=#! /bin/bash
        # Install dependencies
        apt-get update
        apt-get install -y git docker.io docker-compose

        # Enable and start Docker
        systemctl enable docker
        systemctl start docker

        # Add current user to docker group
        usermod -aG docker \$USER

        # Clone the HotLabel infrastructure repository
        git clone https://github.com/Hotoro-Cloud/hotlabel-infra.git /opt/hotlabel
        cd /opt/hotlabel

        # Start the infrastructure
        docker-compose up -d
        "
    
    # Create firewall rules if they don't exist
    if ! gcloud compute firewall-rules describe "allow-http" &> /dev/null; then
        gcloud compute firewall-rules create "allow-http" \
            --allow=tcp:80,tcp:8000,tcp:8001,tcp:8080 \
            --target-tags="http-server" \
            --description="Allow HTTP traffic"
    fi

    if ! gcloud compute firewall-rules describe "allow-https" &> /dev/null; then
        gcloud compute firewall-rules create "allow-https" \
            --allow=tcp:443,tcp:8443,tcp:8444 \
            --target-tags="https-server" \
            --description="Allow HTTPS traffic"
    fi

    if ! gcloud compute firewall-rules describe "allow-grafana" &> /dev/null; then
        gcloud compute firewall-rules create "allow-grafana" \
            --allow=tcp:3000 \
            --target-tags="http-server" \
            --description="Allow Grafana traffic"
    fi
fi

# Get the external IP of the instance
EXTERNAL_IP=$(gcloud compute instances describe "$INSTANCE_NAME" --zone="$ZONE" --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "Deployment completed successfully!"
echo "Instance External IP: $EXTERNAL_IP"
echo ""
echo "Access your services at:"
echo "API Gateway: http://$EXTERNAL_IP:8000"
echo "Kong Admin: http://$EXTERNAL_IP:8001"
echo "Grafana: http://$EXTERNAL_IP:3000 (admin/admin)"
echo "Prometheus: http://$EXTERNAL_IP:9090"
echo ""
echo "SSH into the instance:"
echo "gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
