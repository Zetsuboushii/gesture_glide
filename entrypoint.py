import click

from gesture_glide.config import load_config
from gesture_glide.engine_controller import EngineController
from gesture_glide.gui import run_gui


@click.command()
def main():
    config = load_config()
    engine_controller = EngineController(config)
    engine_controller.run()

    run_gui(engine_controller)

    engine_controller.stop()
    exit(0)

if __name__ == '__main__':
    main()
