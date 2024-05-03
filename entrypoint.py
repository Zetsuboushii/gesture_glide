import click

from gesture_glide.config import load_config
from gesture_glide.engine_controller import EngineController


@click.command()
def main():
    config = load_config()
    controller = EngineController(config)
    controller.run()


if __name__ == '__main__':
    main()
