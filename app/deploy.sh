#!/bin/bash

#SERVICE_NAME="teachmenow-0220" # Define your service name here
#SERVICE_NAME="teachmenow-0117" # Define your service name here
SERVICE_NAME="minoo"  # Define your service name here

# Step 1: Build and push the container image
gcloud builds submit --tag gcr.io/teachmemedical/${SERVICE_NAME} .

# Step 2: Deploy the Cloud Run service with unauthenticated access
gcloud run deploy ${SERVICE_NAME} \
    --image=gcr.io/teachmemedical/${SERVICE_NAME} \
    --vpc-connector dev-connector \
    --region=us-east1 \
    --allow-unauthenticated \
    --platform managed \
    --project teachmemedical \
    --quiet
