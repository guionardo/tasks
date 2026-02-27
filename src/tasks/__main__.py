from tasks.tui.app import MainApp
from tasks.tui.args import get_args
from tasks.tui.context import setup_context


def main():
    config_path, tasks_directory, log_level, log_file = get_args()
    setup_context(config_path, tasks_directory, log_level, log_file)
    app = MainApp()
    app.run()


if __name__ == '__main__':
    main()
