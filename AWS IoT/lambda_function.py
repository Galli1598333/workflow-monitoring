 
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    #Parse your JSON message and get out all your attributes
    tire_size = event["queryResult"]["parameters"]["tires"]
    tire_size = tire_size[:2]

    print("Tire size requested:", tire_size)
    
    #Accessing DB to check for existence
    dynamodb = boto3.client('dynamodb')

    db_response = dynamodb.get_item(TableName='stock', Key={'inches':{'N': str(tire_size)}})
    try:
        #Found an item corresponding to the size requested
        item = db_response['Item']
        print("Found model:", item["model"]["S"])
        model = item["model"]["S"]
        
        #Preparing the response for Google Dialogflow
        response = { "payload": 
            {
            "google": {
                    "expectUserResponse": "true",
                    "richResponse": {
                        "items": [
                        {
                            "simpleResponse": {
                            "textToSpeech": "Here's what I got Gianluca"
                            }
                        },
                        {
                            "basicCard": {
                                "title": str(tire_size) +"inches tires - "+ model,
                                "image": {
                                "url": "https://di-uploads-pod4.dealerinspire.com/mercedesbenzbrampton/uploads/2017/05/mercedes-benz-tires.jpg",
                                "accessibilityText": "Cool tires"
                                },
                            "imageDisplayOptions": "WHITE"
                            }
                        }
                        ]
                    }
                }
            }
        }
    
    except KeyError as e:
        
        #Couldn'find a correct model for the size
        print("Couldn't find anything")
        
        #Preparing the response for Google Dialogflow
        quantity = 50
        response = { "payload": 
            {
            "google": {
                    "expectUserResponse": "true",
                    "richResponse": {
                        "items": [
                        {
                            "simpleResponse": {
                            "textToSpeech": "The item you requested is out of stock, I placed an order for you"
                            }
                        },
                        {
                            "basicCard": {
                                "title": str(quantity)+ " "+ str(tire_size) +"inches tires were ordered",
                                "image": {
                                "url": "https://di-uploads-pod4.dealerinspire.com/mercedesbenzbrampton/uploads/2017/05/mercedes-benz-tires.jpg",
                                "accessibilityText": "Cool tires"
                                },
                            "imageDisplayOptions": "WHITE"
                            }
                        }
                        ]
                    }
                }
            }
        }
        
        #notifying the order to aws-iot
        client = boto3.client('iot-data', region_name='us-east-2')
        client.publish(
            topic='iot/outOfStock',
            qos=0,
            payload=json.dumps({"inches":int(tire_size), "quantity":quantity})
        )
        

    return response 

