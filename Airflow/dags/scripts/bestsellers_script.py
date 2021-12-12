def run_zipfile_downloader(**context):
    '''
    Download the requested zip file into the specified S3 bucket.
    smart_open is a Python 3 library for efficient streaming of very
    large files from/to storages such as S3.
    It handles partial downloads and uses multipart uplaod mechanism.
    Use execution time as partition key.
        Parameters:
            bucket_dir: str
            file_url: str
            ts_nodash: str
        Examples:
            >>> run_zipfile_downloader(
                bucket_dir="s3://mybucket",
                file_url="http://sample/myfile.gz",
                ts_nodash="20211215T220000"
                )
            uploaded file URL:
            s3://mybucket/downloaded_at=2021121522/myfile.gz
    '''
    import logging
    import os
    from smart_open import open
    from .utils.common import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

    logger = logging.getLogger(__name__)
    logger.info(f'params: {context}')

    try:
        bucket_dir = context.get('bucket_dir')
        bucket_dir = f's3://{AWS_ACCESS_KEY_ID}:{AWS_SECRET_ACCESS_KEY}@' + bucket_dir.replace('s3://', '')
        file_url = context.get('file_url')
        ts_nodash = context.get('ts_nodash').replace('T', '')[:10]  # 20211210T075000 > 2021121007
        object_key_to_store = f'downloaded_at={ts_nodash}/' + os.path.basename(file_url)

        logger.info(f'file_url: {file_url}')
        logger.info(f'object_key_to_store: {object_key_to_store}')

        with open(file_url, "rb") as fin:
            with open(os.path.join(bucket_dir, object_key_to_store), "wb") as fout:
                for line in fin:
                    l = [i.strip() for i in line.decode().split("\t")]
                    string = "\t".join(l) + "\n"
                    fout.write(string.encode())

        logger.info('Downloaded successfully')

    except Exception as e:
        message = f"Error in run_zipfile_downloader: {e} \n params: {context}"
        logger.error(message)
        raise RuntimeError(message)


def run_query_on_redshift(**context):
    '''
    Run specified queries on the Redshift cluster.
    :param sqls: list[str]
    '''
    import boto3
    import logging
    import time
    from .utils.common import (
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        REDSHIFT_CLUSTER_IDENTIFIER,
        DATABASE_NAME,
        DATABASE_USER,
        )

    logger = logging.getLogger(__name__)
    logger.info(f'params: {context}')
    sqls = context.get('sqls')

    try:
        client = boto3.client(service_name='redshift-data',
                              region_name='us-east-1',
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        sqls = context.get('sqls')

        result = []
        for sql in sqls:
            result.append(client.execute_statement(
                ClusterIdentifier=REDSHIFT_CLUSTER_IDENTIFIER,
                Database=DATABASE_NAME,
                DbUser=DATABASE_USER,
                Sql=sql))
            time.sleep(5)

        logger.info(f'result: {result}')

    except Exception as e:
        message = f"Error in run_query_on_redshift: {e} \n params: {context}"
        logger.error(message)
        raise RuntimeError(message)
