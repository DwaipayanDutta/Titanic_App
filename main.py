from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

app = FastAPI(title="Titanic Survival Predictor")
# Load trained model and original dataset
# model_response = requests.get(MODEL_URL)
# model = joblib.load(BytesIO(model_response.content))
model = joblib.load("model/titanic_model.pkl")
LOOKUP_DF = pd.read_csv(
    "https://raw.githubusercontent.com/DwaipayanDutta/Titanic_App/refs/heads/main/Data/titanic.csv"
)
LOOKUP_DF = LOOKUP_DF[
    ["PassengerId", "Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]
]
LOOKUP_DF["Embarked"] = LOOKUP_DF["Embarked"].fillna(LOOKUP_DF["Embarked"].mode()[0])
LOOKUP_DF["PassengerId"] = LOOKUP_DF["PassengerId"].astype(str)


class PassengerRequest(BaseModel):
    PassengerId: str


@app.get("/")
async def root():
    return {"message": "Healthy"}


@app.get("/model")
async def get_model_info():
    return {
        "model": "Titanic Survival Predictor",
        "version": "1.0",
        "description": "Predicts survival on the Titanic based on passenger data.",
    }


@app.post("/predict")
async def predict_survival(passenger: PassengerRequest):
    # Find the passenger's record in the lookup data
    passenger_data = LOOKUP_DF[LOOKUP_DF["PassengerId"] == passenger.PassengerId]

    if passenger_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Passenger ID {passenger.PassengerId} not found in records",
        )

    try:
        features = passenger_data.drop("PassengerId", axis=1)
        # Predict survival status using the model
        prediction = model.predict(features)
        survival_status = "Survived" if prediction[0] == 1 else "Not Survived"
        # Return prediction with relevant details
        return {
            "passenger_id": passenger.PassengerId,
            "survival_status": survival_status,
            "features": features.iloc[0].to_dict(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
