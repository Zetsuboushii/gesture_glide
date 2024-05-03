import click

from gesture_glide.engine_controller import EngineController


@click.command()
def main():
    controller = EngineController()
    controller.run()


if __name__ == '__main__':
    main()
