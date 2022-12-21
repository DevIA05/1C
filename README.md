# Benchmark

## Lecture du fichier
**Read csv with dask**: 0.1564185619354248 sec  
```dd.read_csv(csv_file, delimiter=',', encoding= 'unicode_escape')```  
**Read csv with pandas (with chunksize)**: 0.022058725357055664 sec  
```pd.read_csv(csv_file, chunksize=300000, delimiter=',', encoding= 'unicode_escape')```  
**Read pandas.read_csv**: 0.3900887966156006 sec
```pd.read_csv(csv_file, delimiter=',', encoding= 'unicode_escape')```
**Read csv with dask (with chunksize)**: 0.1851048469543457 sec  
```dd.read_csv(csv_file,blocksize=25e6, delimiter=',', encoding= 'unicode_escape')```