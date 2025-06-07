import click
from sourcesherpa.extractors.dummy_extractor import extract_dummy
from sourcesherpa.storage.mongo import MongoContextSource

@click.group()
def cli():
    pass

@cli.command()
def extract_and_load():
    blocks = extract_dummy()
    mongo = MongoContextSource("mongodb://localhost:27017", "sourcesherpa")
    mongo.write_blocks(blocks)
    click.echo("Dummy blocks extracted and loaded!")

if __name__ == "__main__":
    cli()
