import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db=redis.Redis(host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_DB_ID)


# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = ResNet50(weights="imagenet", include_top=True)


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    img_path=os.path.join(settings.UPLOAD_FOLDER, image_name)
    img=image.load_img(img_path, target_size=(224,224))
    img_array=image.img_to_array(img)
    img_batch=np.expand_dims(img_array,axis=0)
    img_ready=preprocess_input(img_batch)
    prediction = model.predict(img_ready, verbose=0)
    decoded = decode_predictions(prediction, top=1)
    class_name = decoded[0][0][1]
    prob = float(decoded[0][0][2])
    pred_probability = round(prob, 4) 
    # TODO: Implement the code to predict the class of the image_name


    
    # Load image

    # Apply preprocessing (convert to numpy array, match model input dimensions (including batch) and use the resnet50 preprocessing)

    # Get predictions using model methods and decode predictions using resnet50 decode_predictions
  

    # Convert probabilities to float and round it

    return class_name, pred_probability


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # TODO
        # Take a new job from Redis

        # Decode the JSON data for the given job

        # Important! Get and keep the original job ID

        # Run the loaded ml model (use the predict() function)

        # Prepare a new JSON with the results
        job=db.brpop(settings.REDIS_QUEUE)
        job_data=job[1].decode("utf-8")
        job_dict=json.loads(job_data)
        job_id=job_dict["id"]
        image_name=job_dict["image_name"]

        predict_image=predict(image_name)

        class_name, probability=predict_image

        output = {"prediction": class_name, "score": probability}
        output_str=json.dumps(output)
        db.set(job_id,output_str)



        # Store the job results on Redis using the original
        # job ID as the key

        # Sleep for a bit
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
