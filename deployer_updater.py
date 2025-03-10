import logging
import time
from datetime import datetime

import boto3
import requests
from botocore.exceptions import ClientError
from croniter import croniter
from dotenv import load_dotenv

load_dotenv()

# Configuration
REGION = 'us-east-1'  # Change as needed
ENDPOINT_URL = 'https://your-api-endpoint.com/success'  # Replace with your actual endpoint
APPLICATION_NAME = 'your-application-name'  # Replace with your CodeDeploy application name

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AWS CodeDeploy client
codedeploy = boto3.client('codedeploy', region_name=REGION)

def update_deployment_status():
    try:
        # List all deployments in READY state
        deployment_ids = get_ready_deployments()
        
        if not deployment_ids:
            logger.info("No deployments in Ready state found")
            return
        
        # Update each Ready deployment to Successful
        successful_deployments = []
        for deployment_id in deployment_ids:
            try:
                # Get deployment details
                deployment_info = codedeploy.get_deployment(
                    deploymentId=deployment_id
                )
                
                # Update deployment status to Successful
                codedeploy.update_deployment(
                    deploymentId=deployment_id,
                    targetStatus='Successful'
                )
                
                successful_deployments.append(deployment_id)
                # print(f"Successfully updated deployment {deployment_id} to Successful")
                logger.info(f"Successfully updated deployment {deployment_id} to Successful")
                
            except ClientError as e:
                # print(f"Error updating deployment {deployment_id}: {str(e)}")
                logger.error(f"Error updating deployment {deployment_id}: {str(e)}")
        
        if successful_deployments:
            logger.info(f"Updated {len(successful_deployments)} deployments to Successful")
            
    except ClientError as e:
        logger.error(f"Error listing deployments: {str(e)}")

def make_api_call():
    try:
        # Prepare payload with current timestamp
        payload = {
            'timestamp': datetime.now().isoformat(),
            'message': 'Deployment status update completed'
        }
        
        # Make POST request
        response = requests.post(
            ENDPOINT_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        response.raise_for_status()
        logger.info(f"Successfully made POST request. Status code: {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making POST request: {str(e)}")

def schedule_tasks():
    # Define the cron schedule for 4PM EST daily
    cron_expression = '0 16 * * *'  # 4PM daily

    # Get the current time in UTC
    now = datetime.now()

    # Create a croniter object
    cron = croniter(cron_expression, now)

    while True:
        # Get the next scheduled time
        next_run = cron.get_next(datetime)

        # Calculate the sleep duration until the next run
        sleep_duration = (next_run - datetime.now()).total_seconds()

        # Sleep until the next scheduled time
        if sleep_duration > 0:
            time.sleep(sleep_duration)

        # Execute the task
        make_api_call()

        # Log the execution
        logger.info(f"Task executed at {datetime.now()}")

def get_ready_deployments():
    """Get all deployments in READY state"""
    try:
        logger.info("Retrieving deployments in READY state...")
        client = boto3.client('codedeploy')
        
        deployments = []
        paginator = client.get_paginator('list_deployments')
        
        for page in paginator.paginate():
            batch_deployments = client.batch_get_deployments(
                deploymentIds=page['deployments']
            )
            
            for deployment in batch_deployments['deploymentsInfo']:
                if deployment['status'] == 'READY':
                    deployments.append(deployment['deploymentId'])
        
        logger.info(f"Found {len(deployments)} deployments in READY state")
        return deployments
        
    except Exception as e:
        logger.error(f"Error retrieving ready deployments: {str(e)}")
        return []


def main():
    try:
        # Initial run to update deployments
        print(f"Starting deployment status update at {datetime.now()}")
        update_deployment_status()
        
        # Schedule the daily API call
        schedule_tasks()
        
        # Keep the script running
        while True:
            pass
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    # Configure AWS credentials (should be set up in ~/.aws/credentials or environment variables)
    boto3.setup_default_session(region_name=REGION)
    main()