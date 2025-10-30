import json
import time
from uuid import uuid4

import redis

from .. import settings

# Connect to Redis using settings from `settings.py`
# host, port and db id are available as REDIS_IP, REDIS_PORT, REDIS_DB_ID
db = redis.Redis(host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_DB_ID)


async def model_predict(image_name):
    print(f"Processing image {image_name}...")
    """
    Receives an image name and queues the job into Redis.
    Will loop until getting the answer from our ML service.

    Parameters
    ----------
    image_name : str
        Name for the image uploaded by the user.

    Returns
    -------
    prediction, score : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    prediction = None
    score = None

    # Assign an unique ID for this job and add it to the queue.
    # We need to assign this ID because we must be able to keep track
    # of this particular job across all the services
    job_id = str(uuid4())

    # Create a dict with the job data we will send through Redis having the
    # following shape:
    # {
    #    "id": str,
    #    "image_name": str,
    # }
    job_data = {"id": job_id, "image_name": image_name}

    # Send the job to the model service using Redis
    # Using Redis `lpush()` to push a JSON-encoded job into the queue
    db.lpush(settings.REDIS_QUEUE, json.dumps(job_data))

    # Loop until we received the response from our ML model
    while True:
        # Attempt to get model predictions using job_id
        # Use `get()` to check whether the model service stored the results
        output = db.get(job_id)

        # Check if the text was correctly processed by our ML model
        # Don't modify the code below, it should work as expected
        if output is not None:
            # Redis returns bytes; decode and parse JSON
            output = json.loads(output.decode("utf-8"))
            prediction = output["prediction"]
            score = output["score"]

            # Clean up the key now that we've retrieved the result
            db.delete(job_id)
            break

        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)

    return prediction, score
