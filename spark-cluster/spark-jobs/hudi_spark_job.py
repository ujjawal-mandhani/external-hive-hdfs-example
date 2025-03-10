from datetime import datetime
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys

def getResolvedOptions_locally(sys_arguments, to_find_array):
    final_data = {}
    final_returned_data = {}
    for i in range(1, len(sys_arguments), 2):
        final_data[sys_arguments[i].replace('--', '')] = sys_arguments[i+1]
    for item in to_find_array:
        final_returned_data[item] = final_data.get(item)
    return final_returned_data


full_load_param = getResolvedOptions_locally(sys.argv, ['full_load'])["full_load"]
merge_or_copy__write_param = getResolvedOptions_locally(sys.argv, ['merge_or_copy__write'])["merge_or_copy__write"]

if merge_or_copy__write_param in [None, '']:
    merge_or_copy__write_param = "MERGE_ON_READ"

table_name = "geographic_units_by_industry_and_statistical_area_hudi" + "_" + merge_or_copy__write_param.lower()

spark = SparkSession.builder \
    .appName("Hudi Example") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.warehouse.dir", "hdfs://namenode:8020/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://metastore:9083") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
# spark.sparkContext.setLogLevel("INFO")

print("::::::::::::::", full_load_param)
print("::::::::::::::", merge_or_copy__write_param)




df = spark.read.option("header", "true").csv("./geographic_units_by_industry_and_statistical_area.csv")

df = df.withColumn("compositekey", expr("concat_ws('_', Area, anzsic06, year)")).withColumn("created_at", lit(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))) \
    .withColumn("created_at", expr("cast(created_at as timestamp)"))\
    .withColumn("year_created", expr("year(created_at)")).withColumn("month", expr("month(created_at)")) \
    .withColumn("date", expr("date(created_at)"))

print(":::::::::::::Total count", df.count())
if full_load_param == 'N':
    df = df.limit(5)
    df.show(10, truncate=False)

elif full_load_param == 'D':
    df = df.limit(5)
    df.show(10, truncate=False)


hudi_options = {
    "hoodie.table.name": f"{table_name}",
    "hoodie.datasource.write.recordkey.field": "compositekey",
    "hoodie.datasource.write.precombine.field": "created_at",
    "hoodie.datasource.write.partitionpath.field": "year_created,month,date",  # Leave empty if no partitions
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.write.table.type": merge_or_copy__write_param,  # "COPY_ON_WRITE", MERGE_ON_READ
    "hoodie.datasource.write.hive_style_partitioning": "true",
    "hoodie.datasource.hive_sync.enable": "true",
    "hoodie.datasource.hive_sync.database": "default",
    "hoodie.datasource.hive_sync.table": f"{table_name}",
    # "hoodie.datasource.hive_sync.mode": "jdbc",
    # "hoodie.datasource.hive_sync.jdbcurl": "jdbc:hive2://localhost:10000/default",
    "hoodie.datasource.hive_sync.mode": "hms",  # Use Hive Metastore (Thrift) mode
    "hoodie.datasource.hive_sync.metastore.uris": "thrift://metastore:9083",
    "hoodie.datasource.hive_sync.partition_extractor_class": "org.apache.hudi.hive.MultiPartKeysValueExtractor", # is required for multiple partition keys
    "hoodie.bloom.index.update.partition.path": "true"
}

mode = "append"

if full_load_param == 'Y':
    hudi_options["hoodie.datasource.write.operation"] = "bulk_insert" ## this will only append the data not will check any duplicates
    mode = "overwrite"

if full_load_param == 'D':
    hudi_options["hoodie.datasource.write.operation"] = "delete" ## this will only append the data not will check any duplicates


df.write.format("hudi") \
    .options(**hudi_options) \
    .mode(mode) \
    .save(f"hdfs://namenode:8020/user/hive/warehouse/{table_name}")

"""
spark-submit --packages org.apache.hudi:hudi-spark3.5-bundle_2.12:1.0.0 \
    --conf 'spark.serializer=org.apache.spark.serializer.KryoSerializer' \
    --conf 'spark.sql.extensions=org.apache.spark.sql.hudi.HoodieSparkSessionExtension' \
    --conf 'spark.sql.catalog.spark_catalog=org.apache.spark.sql.hudi.catalog.HoodieCatalog' \
    --conf 'spark.kryo.registrator=org.apache.spark.HoodieSparkKryoRegistrar' \
    --conf spark.driver.memory=3g \
    --conf spark.executor.memory=6g \
    --conf spark.sql.shuffle.partitions=50 \
    hudi_spark_job.py --full_load Y --merge_or_copy__write COPY_ON_WRITE
"""

# spark.sparkContext.setLogLevel("ALL")  # Show everything
# spark.sparkContext.setLogLevel("DEBUG")  # Debug logs
# spark.sparkContext.setLogLevel("INFO")  # Default logs
# spark.sparkContext.setLogLevel("WARN")  # Hide INFO logs
# spark.sparkContext.setLogLevel("ERROR")  # Show only errors
# spark.sparkContext.setLogLevel("FATAL")  # Show critical failures only