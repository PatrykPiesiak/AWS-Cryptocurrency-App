import pandas as pd
import boto3
from botocore.exceptions import ClientError
import logging
import json
import urllib3
import os

API_KEY = os.environ.get('API_KEY')
FILE_NAME = os.environ.get('FILE_NAME')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
SERVER_URL = os.environ.get('SERVER_URL')

logging.basicConfig(level=logging.INFO)


def fetch_data():
    http = urllib3.PoolManager()

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    parameters = {
        'limit': 10,
        'convert': 'USD'
    }

    try:
        url = f"{SERVER_URL}?limit={parameters['limit']}&convert={parameters['convert']}"
        response = http.request('GET', url, headers=headers)
        data = json.loads(response.data.decode('utf-8'))
        crypto_data = data['data']
    except urllib3.exceptions.RequestError as e:
        print(e)
        return None

    crypto_list = []

    for coin_info in crypto_data:
        quote = coin_info['quote']['USD']
        crypto_list.append({
            'name': coin_info['name'],
            'symbol': coin_info['symbol'],
            'price': quote['price'],
            'volume_24h': quote['volume_24h'],
            'volume_change_24h': quote['volume_change_24h'],
            'percent_change_1h': quote['percent_change_1h'],
            'percent_change_24h': quote['percent_change_24h'],
            'percent_change_7d': quote['percent_change_7d'],
            'percent_change_30d': quote['percent_change_30d']
        })

    df = pd.DataFrame(crypto_list)

    csv_data = df.to_csv(index=False)

    return csv_data


def save_data_to_s3(data, s3_bucket_name, s3_key):
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data, ContentType='text/csv')
    except ClientError as e:
        logging.error(f'Error in save_data_to_s3: {str(e)}')
        raise


def main():
    logging.info('Fetching data...')
    data = fetch_data()

    logging.info(f'Uploading data to S3 bucket {S3_BUCKET_NAME}...')
    save_data_to_s3(data, S3_BUCKET_NAME, FILE_NAME)


def lambda_handler(event, context):
    try:
        main()
        return {'statusCode': 200}
    except Exception as e:
        logging.error(f'Lambda execution error: {str(e)}')
        return {'statusCode': 500, 'body': str(e)}


if __name__ == '__main__':
    main()