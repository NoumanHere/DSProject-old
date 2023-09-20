import pandas as pd
from pycaret.regression import load_model, predict_model
from flask import Flask, request, jsonify, render_template
import os
from azure.storage.blob import BlobServiceClient

# 2. Create the app object
app = Flask(__name__, template_folder='static')

storage_account_key = "PK8zHr5xPaDmBLj6h9QPpOED4cZ/eQUTzfp5WDC7sUsV9pSdXpENI5t5S3RqRt2mgmnR/EL6Dy9b+ASt2TgIsQ=="
storage_account_name = "model23"
connection_string = "DefaultEndpointsProtocol=https;AccountName=model23;AccountKey=PK8zHr5xPaDmBLj6h9QPpOED4cZ/eQUTzfp5WDC7sUsV9pSdXpENI5t5S3RqRt2mgmnR/EL6Dy9b+ASt2TgIsQ==;EndpointSuffix=core.windows.net"
container_name = "modelcontainer"

# Replace with your connection string

# Replace with the container and blob names you want to access
container_name = "modelblob"
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

def remove_spaces(text):
    text = str(text)
    return text.strip()


@app.route('/')
def main():
    return render_template('index.html')


# Define predict function
@app.route('/predict', methods=['POST'])
def upload_csv():
    try:
        csv_file = request.files.get('csv_file')

        if not csv_file:
            return "No file provided", 400

        filename = csv_file.filename
        df = pd.read_csv(csv_file)

        # Check if 'Carrier Pay' column exists in the DataFrame
       # if 'Carrier Pay' not in df.columns:
            # If not, create a new column 'Carrier Pay' by multiplying 'Miles' and 'RPM'
       #     df['Carrier Pay'] = df['Miles'] * df['RPM']

        for col in ['Origin City', 'Origin State', 'Delivery City', 'Delivery State', 'Origin KMA', 'Delivery KMA']:
            df[col] = df[col].apply(remove_spaces)

        # LANE feature generation
        df['LANE'] = df['Origin City'] + [', '] * df.shape[0] + df['Origin State'] + ['-'] * df.shape[0] + df['Delivery City'] + [', '] * df.shape[0] + df['Delivery State']

        test = predict_model(model, data=df)

        # Exclude a specific column from the response
        #column_to_exclude = 'Carrier Pay'
       # if column_to_exclude in test.columns:
       #     test = test.drop(columns=[column_to_exclude])

        return test.to_json(orient="records")

    except Exception as e:
        return str(e), 500

@app.route('/predict_json', methods=['POST'])
def predict_json():
    json_data = request.get_json()
    check = 0 
    if json_data:
        try:
            df = pd.DataFrame(json_data)
            # Check if 'Carrier Pay' column exists in the DataFrame
           # if 'Carrier Pay' not in df.columns:
                # If not, create a new column 'Carrier Pay' by multiplying 'Miles' and 'RPM'
           #     df['Carrier Pay'] = df['Miles'] * df['RPM']
        #    check = 1

            for col in ['Origin City', 'Origin State','Delivery City', 'Delivery State', 'Origin KMA', 'Delivery KMA']:
                df[col] = df[col].apply(remove_spaces)
                
            # LANE feature generation
            df['LANE'] = df['Origin City'] + [', ']*(df.shape[0]) + df['Origin State'] + ['-']*(df.shape[0]) +  df['Delivery City'] + [', ']*(df.shape[0]) + df['Delivery State']

            test = predict_model(model, data=df)

            # Exclude a specific column from the response
           # column_to_exclude = 'Carrier Pay'
           # if check == 1:
            #    test = test.drop(columns=[column_to_exclude])


            return test.to_json(orient="records")

        except Exception as e:
            return str(e), 500

    return "No JSON data provided", 400

if __name__ == "__main__":
    app.run()
