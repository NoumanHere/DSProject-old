import pandas as pd
from pycaret.regression import load_model, predict_model
from flask import Flask, request, jsonify, render_template
import os
from azure.storage.blob import BlobServiceClient

# 2. Create the app object
app = Flask(__name__, template_folder='static')

# Replace with your connection string
connection_string = "DefaultEndpointsProtocol=https;AccountName=grml23;AccountKey=PO1VY2bNJNknpEeFW31hgE4vH7kHpVhcQjPSdY5wkOPZq9zImPjWptm1Pd/JPV8Y4fqL522bxsGe+ASt58y/pA==;EndpointSuffix=core.windows.net"

# Replace with the container and blob names you want to access
container_name = "grml23"
blob_name = "PyC_MASTER_MAY_11_Low_Miles_NO-RPM"

# Replace with the local folder path where you want to store the downloaded file
local_folder_path = "model"

if not os.path.exists(local_folder_path):
    os.makedirs(local_folder_path)
    print(f"Directory '{local_folder_path}' has been created.")
else:
    print(f"Directory '{local_folder_path}' already exists.")

#Download the model

model_path = local_folder_path + '/' + blob_name + '.pkl'
print(model_path)

if not os.path.exists(model_path):
    print('Doesnt exist')
    # Initialize BlobServiceClient using the connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # Get a reference to the blob
    model_name = blob_name + '.pkl' 
    blob_client = container_client.get_blob_client(model_name)
    print(blob_client)

    # Download the blob content to a local file
    with open(model_path, "wb") as local_file:
        print(model_name)
        blob_data = blob_client.download_blob()
        blob_data.readinto(local_file)

    print(f"Blob '{blob_name}' downloaded and saved to '{local_folder_path}/{blob_name}'.")
else:
    print('Model exist')

# 3. Load trained Pipeline

model = load_model(local_folder_path + '/' + blob_name)


@app.route('/')
def main():
    return render_template('index.html')


# Define predict function
@app.route('/predict', methods=['POST'])
def upload_csv():
    csv_file = request.files.get('csv_file')
    
    if csv_file:
        filename = csv_file.filename
        df = pd.read_csv(csv_file)
        # Check if 'Carrier Pay' column exists in the DataFrame
        if 'Carrier Pay' not in df.columns:
            # If not, create a new column 'Carrier Pay' by multiplying 'Miles' and 'RPM'
            df['Carrier Pay'] = df['Miles'] * df['RPM']


        test = predict_model(model, data=df)

        # Exclude a specific column from the response
        column_to_exclude = 'Carrier Pay'
        if column_to_exclude in df.columns:
            df = df.drop(columns=[column_to_exclude])

        return test.to_json(orient="records")

    return "No file provided", 400

@app.route('/predict_json', methods=['POST'])
def predict_json():
    json_data = request.get_json()

    if json_data:
        try:
            df = pd.DataFrame(json_data)
            # Check if 'Carrier Pay' column exists in the DataFrame
            if 'Carrier Pay' not in df.columns:
                # If not, create a new column 'Carrier Pay' by multiplying 'Miles' and 'RPM'
                df['Carrier Pay'] = df['Miles'] * df['RPM']

            test = predict_model(model, data=df)

            # Exclude a specific column from the response
            column_to_exclude = 'Carrier Pay'
            if column_to_exclude in df.columns:
                df = df.drop(columns=[column_to_exclude])


            return test.to_json(orient="records")

        except Exception as e:
            return str(e), 400

    return "No JSON data provided", 400

if __name__ == "__main__":
    app.run()
