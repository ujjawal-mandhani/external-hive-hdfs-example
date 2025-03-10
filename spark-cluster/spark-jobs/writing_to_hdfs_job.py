from datetime import datetime
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Initialize Spark session with Hive support and remote HDFS
spark = SparkSession.builder \
    .appName("Spark HDFS Hive Integration") \
    .config("spark.sql.warehouse.dir", "hdfs://namenode:8020/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://metastore:9083") \
    .enableHiveSupport() \
    .getOrCreate()

df = spark.read.option("header", "true").csv("./annual_enterprise_survey.csv")

df = df.withColumn("value", expr("cast(value as bigint)")).withColumn("created_at", lit(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))) \
    .withColumn("created_at", expr("cast(created_at as timestamp)")).withColumn("year", expr("cast(year as int)"))

df.write.mode("overwrite").parquet("hdfs://namenode:8020/user/hive/warehouse/annual_enterprise_survey")


spark.sql("drop table if exists annual_enterprise_survey")

hive_schema = []

final_json_schema = json.loads(df.schema.json())
for item in final_json_schema['fields']:
    if item["type"] == 'long':
        hive_schema.append(item["name"] + ' ' + 'bigint')
    else:
        hive_schema.append(item["name"] + ' ' + item["type"])
    
cols_from_hive_arry = ', \n'.join(hive_schema)

print(cols_from_hive_arry)


spark.sql(f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS annual_enterprise_survey (
        {cols_from_hive_arry}
    )
    STORED AS PARQUET
    LOCATION 'hdfs://namenode:8020/user/hive/warehouse/annual_enterprise_survey'
""")
