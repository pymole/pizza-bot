from communicators import Communicator
import config


def main(communicator: Communicator):
    communicator.start()


if __name__ == '__main__':
    main(config.communicator)
