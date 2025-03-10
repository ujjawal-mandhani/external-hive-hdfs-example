UI where can you see the tables are created in HDFS - 

http://0.0.0.0:9870/explorer.html#/user/hive/warehouse/annual_enterprise_survey

CLI method for above 

hdfs dfs -ls /user/hive/warehouse

HDFS directories like /opt/hadoop/data/nameNode and /opt/hadoop/data/dataNode are internal and handle metadata and data block storage for HDFS.

User-level data written by applications like Spark is stored in directories like /user/hive/warehouse in HDFS.

The /user/hive/warehouse directory is the location used by Hive (and Spark when connected to Hive) for storing tables.

```sql
show create table mytable
select * from mytable
```

Csv files has been dowloaded from given link and placed in spark-cluster/spark-jobs/annual_enterprise_survey.csv

- https://www.stats.govt.nz/assets/Uploads/Annual-enterprise-survey/Annual-enterprise-survey-2023-financial-year-provisional/Download-data/annual-enterprise-survey-2023-financial-year-provisional.csv
- https://www.stats.govt.nz/assets/Uploads/New-Zealand-business-demography-statistics/New-Zealand-business-demography-statistics-At-February-2024/Download-data/geographic-units-by-industry-and-statistical-area-2000-2024-descending-order.zip


https://repo1.maven.org/maven2/org/apache/hudi/hudi-spark3.5-bundle_2.12/
https://hudi.apache.org/docs/quick-start-guide/


```bash 
docker cp spark-master:/root/.ivy2/cache ./spark-cluster/.ivy2/cache


beeline -u jdbc:hive2://hiveserver2:10000/default
ADD JAR file:///opt/hive/lib/hudi-hadoop-mr-bundle-1.0.0.jar;


hdfs dfs -put /opt/hive/lib/hudi-hadoop-mr-bundle-1.0.0.jar /user/hive/lib/
```


### Issue 

Unable to count the rows in table after setting below params it started working

SET hive.vectorized.execution.enabled = false;
SET hive.execution.engine=mr;
