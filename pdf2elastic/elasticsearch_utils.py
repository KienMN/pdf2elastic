import logging
from typing import Any, Generator

import extract_content
from elasticsearch import Elasticsearch, helpers

logger = logging.getLogger(__name__)

MAX_ITEMS = None


def genrate_data(
    file_path: str, index_name: str
) -> Generator[dict[str, Any], None, None]:
    """Generate data for inserting to Elasticsearch"""
    i = 0
    for p in extract_content.extract(file_path):
        i += 1
        yield {"_index": index_name, **p.model_dump()}
        if MAX_ITEMS is not None:
            if i == MAX_ITEMS:
                return


def get_http_auth():
    """Get credentials for Elasticsearch client"""
    # Can use more secured function
    username = "elastic"
    password = "elastic@123"
    return username, password


def get_elastic_client(host: str = "http://localhost:9200/") -> Elasticsearch:
    client = Elasticsearch(host, http_auth=get_http_auth())
    logging.info(client.info())
    return client


def insert_data(file_path: str, index_name: str, batch_size: int) -> None:
    """Insert data to Elasticsearch"""
    client = get_elastic_client()
    count = 0
    failed = 0

    for success, info in helpers.parallel_bulk(
        client, genrate_data(file_path, index_name), chunk_size=batch_size
    ):
        if success:
            count += 1
        else:
            failed += 1
            logger.error("Unsuccess item: %s", info)

    logger.info(
        "Finish inserting %d documents. Failed %d documents.", count, failed
    )


def search_keyword(keyword: str, index: str, size: int) -> list[dict]:
    """Search document given the keyword"""
    client = get_elastic_client()
    query = {"query": {"match": {"text": f"{keyword}"}}, "size": f"{size}"}
    hits = None
    try:
        response = client.search(index=index, body=query)
        hits = response["hits"]["hits"]
    except Exception as e:
        logger.exception(e)
    return hits
