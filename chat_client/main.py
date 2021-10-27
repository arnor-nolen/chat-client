from auth import login
from rich import print
from rich.traceback import install
from settings import settings

install()

if __name__ == '__main__':
    token = login(
        email=settings.email, password=settings.password.get_secret_value()
    )
    print(f'{token=}')
