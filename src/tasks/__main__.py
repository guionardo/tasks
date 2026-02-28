from tasks.service.logging_service import get_logger
from tasks.tui.app import MainApp
from tasks.tui.args import get_args
from tasks.tui.context import setup_context


def main():
    config_path, tasks_directory, log_level, log_file = get_args()
    setup_context(config_path, tasks_directory, log_level, log_file)
    try:
        app = MainApp()

        app.run()
    except Exception as e:
        get_logger(__name__).error('App crashed - %s', e)
        raise e


if __name__ == '__main__':
    main()
