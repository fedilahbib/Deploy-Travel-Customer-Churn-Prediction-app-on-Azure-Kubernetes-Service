import os
import joblib
import uvicorn
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI(debug=False)

# Load the model from the file
model = joblib.load('app/model.pkl')

DATABASE_HOST= os.environ.get('ME_CONFIG_MONGODB_SERVER')
DATABASE_USERNAME= os.environ.get('ME_CONFIG_MONGODB_ADMINUSERNAME')
DATABASE_PASSWORD= os.environ.get('ME_CONFIG_MONGODB_ADMINPASSWORD')

myclient = MongoClient(DATABASE_HOST,
                     username=DATABASE_USERNAME,
                     password=DATABASE_PASSWORD)


mydb = myclient["churn_db"]
#dummy collection
mycol = mydb["churn_collection"]


class FeatureDataInstance(BaseModel):
    """Define JSON data schema for prediction requests."""
    Age:int 
    AnnualIncomeClass: int
    ServicesOpted: int
    BookedHotel: int
    AccountSyncedToSocialMedia: int
    FrequentFlyer_No_Record: int
    FrequentFlyer_Yes: int


@app.get('/', status_code=200)
def predict():
    return "ok"
    
@app.post('churn_prediction', status_code=200)
def predict(data: FeatureDataInstance):
    prediction = model.predict(np.array([[data.Age,data.AnnualIncomeClass,data.ServicesOpted,data.BookedHotel,data.AccountSyncedToSocialMedia,data.FrequentFlyer_No_Record,data.FrequentFlyer_Yes]]))
    result=data.dict()
    result["churn"]=int(prediction[0])
    mycol.insert_one(result)
    return {'churn': result["churn"]}

@app.get('churn_prediction', status_code=200)
def get_predicted():
    return {'results': list(mycol.find({},{ "_id": 0 }))}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', workers=1)