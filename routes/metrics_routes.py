from typing import Optional
from fastapi import APIRouter, Query
from service.processes import fetch_data_from_bucket

router = APIRouter()

@router.get("/influxdb/fetch")
def get_metrics(
    bucket: str = Query(..., description="InfluxDB bucket name"),
    range_start: str = Query("-1m", description="Flux range start, e.g. -1m"),
    measurement: str = Query(None, description="Measurement name (optional)")
):
    flux_query = f'from(bucket: "{bucket}") |> range(start: {range_start})'
    if measurement:
        flux_query += f' |> filter(fn: (r) => r._measurement == "{measurement}")'
    data = fetch_data_from_bucket(bucket, flux_query)
    return {"data": data}


@router.get("/influxdb/fetch-processes")
def fetch_processes(
    bucket: str = Query(..., description="InfluxDB bucket name"),
    range_start: str = Query("-1m", description="Flux range start, e.g. -1m"),
    host: Optional[str] = Query(None, description="Filter by host")
):
    flux_query = f'from(bucket: "{bucket}") |> range(start: {range_start})'
    if host:
        flux_query += f' |> filter(fn: (r) => r.host == "{host}")'
    data = fetch_data_from_bucket(bucket, flux_query)
    return {"data": data}


@router.get("/influxdb/fetch-host-stats")
def fetch_host_stats(
    bucket: str = Query(..., description="InfluxDB bucket name"),
    range_start: str = Query("-1m", description="Flux range start, e.g. -1m"),
    host: str = Query(..., description="Filter by host")
):
    cpu_query = f'''
        from(bucket: "{bucket}")
        |> range(start: {range_start})
        |> filter(fn: (r) => r._measurement == "cpu" and (r.cpu == "cpu-total" or r.cpu == "cpu0") and r._field == "usage_user" and r.host == "{host}")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n:1)
        |> keep(columns: ["_value"])
    '''
    cpu_data = fetch_data_from_bucket(bucket, cpu_query)
    cpu = cpu_data[0]['_value'] if cpu_data else None

    mem_query = f'''
        from(bucket: "{bucket}")
        |> range(start: {range_start})
        |> filter(fn: (r) => r._measurement == "mem" and r._field == "used_percent" and r.host == "{host}")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n:1)
        |> keep(columns: ["_value"])
    '''
    mem_data = fetch_data_from_bucket(bucket, mem_query)
    memory = mem_data[0]['_value'] if mem_data else None

    disk_query = f'''
        from(bucket: "{bucket}")
        |> range(start: {range_start})
        |> filter(fn: (r) => r._measurement == "diskio" and r.host == "{host}" and r._field == "io_time")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n:1)
        |> keep(columns: ["_value"])
    '''
    disk_data = fetch_data_from_bucket(bucket, disk_query)
    diskio = disk_data[0]['_value'] if disk_data else None

    return {
        "cpu": cpu,
        "memory": memory,
        "diskio": diskio,
        
    }

@router.get("/influxdb/fetch-background-processes")
def fetch_background_processes(
    bucket: str = Query(..., description="InfluxDB bucket name"),
    range_start: str = Query("-1m", description="Flux range start, e.g. -1m"),
    host: Optional[str] = Query(None, description="Filter by host"),
    os_type: Optional[str] = Query("linux", description="OS type: linux or windows")
):
    if os_type.lower() == "windows":
        measurement = "win_process"
        fields_to_keep = [
            "_time", "ID_Process", "Percent_Processor_Time", "Private_Bytes",
            "Thread_Count", "Virtual_Bytes", "Working_Set", "host", "instance", "objectname", "source"
        ]
    else:
        measurement = "procstat"
        fields_to_keep = [
            "_time", "process_name", "cpu_usage", "memory_usage", "user", "pid", "host"
        ]
    keep_clause = f'|> keep(columns: ["' + '", "'.join(fields_to_keep) + '"] )'

    flux_query = f'''
        from(bucket: "{bucket}")
        |> range(start: {range_start})
        |> filter(fn: (r) => r._measurement == "{measurement}"{f' and r.host == "{host}"' if host else ''})
        |> sort(columns: ["_time"], desc: true)
        |> first()
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        {keep_clause}
    '''
    data = fetch_data_from_bucket(bucket, flux_query)
    return {"data": data}








