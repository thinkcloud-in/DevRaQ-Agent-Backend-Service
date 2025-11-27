from Database.influxdb_client import get_influxdb_client

def fetch_data_from_bucket(bucket: str, flux_query: str):
    client = get_influxdb_client()
    query_api = client.query_api()
    result = query_api.query(org=client.org, query=flux_query)
    client.close()
    data = []
    for table in result:
        for record in table.records:
            data.append(record.values) 
    return data