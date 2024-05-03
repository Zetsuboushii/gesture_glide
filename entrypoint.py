import click
from gesture_glide import config

@click.command()
def entrypoint():
    config = config.load_config()
    print(config)

if __name__ == "__main__":
    entrypoint()