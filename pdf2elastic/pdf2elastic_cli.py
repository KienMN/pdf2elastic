import logging

import click
import elasticsearch_utils
import extract_index as ei

# Log format
log_format = "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("file_path", type=click.STRING)
def extract_index(file_path):
    """Extract index from a pdf file"""
    logger.info(file_path)
    index, _ = ei.extract(file_path)
    for heading in index:
        logger.info(heading)


@cli.command()
@click.argument("file_path", type=click.STRING)
@click.argument("index_name", type=click.STRING)
@click.argument("batch_size", type=click.INT, default=500)
def insert_to_elastic(file_path: str, index_name: str, batch_size: int):
    """Insert data from pdf file to elasticsearch"""
    logger.info(file_path)
    logger.info(index_name)
    logger.info(batch_size)
    elasticsearch_utils.insert_data(file_path, index_name, batch_size)


@cli.command()
@click.argument("keyword", type=click.STRING)
@click.argument("index", type=click.STRING)
@click.argument("size", type=click.STRING, default=10)
def search(keyword, index, size):
    """Search a keyword"""
    res = elasticsearch_utils.search_keyword(keyword, index, size)
    logger.info("Number of items: %d.", len(res))
    for r in res:
        logger.info(r)


if __name__ == "__main__":
    cli()
