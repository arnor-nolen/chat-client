from rich.traceback import install
from settings import settings
from client import Client
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.console import Group
from textual.app import App
from textual.widgets import Footer, Placeholder, Header as TxtHeader
from textual import events
from textual.widget import Widget
from textual.reactive import Reactive, watch
from rich.style import StyleType
from rich.repr import Result
from rich.console import RenderableType
from typing import Optional
from datetime import datetime

install()


class Header(TxtHeader):
    def __init__(self, email: Optional[str] = None) -> None:
        super().__init__(style='green')
        self.email = email

    email: Reactive[str]

    def render(self) -> RenderableType:
        header_table = Table.grid(padding=(0, 1), expand=True)
        header_table.style = self.style
        header_table.add_column(justify="left")
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_column("clock", justify="right")
        header_table.add_row(
            f'Logged in as {self.email}' if self.email is not None else '',
            self.full_title,
            self.get_clock() if self.clock else "",
        )
        header = (
            Panel(header_table, style=self.style)
            if self.tall
            else header_table
        )
        return header


class Channels(Widget):
    """Channel selector"""

    def __init__(self, channels: list[dict]) -> None:
        super().__init__()
        self.channels = channels

    selected = Reactive(0)

    def render(self) -> Panel:
        grid = Table.grid(padding=(0, 1))
        grid.add_column(justify='right')
        grid.add_column()
        for channel in self.channels:
            grid.add_row(
                '[white]→[/]'
                if self.channels[self.selected]['id'] == channel['id']
                else '',
                channel['name'],
            )
        return Panel(
            Align.center(
                Group(
                    Align.center('[white]Your channels:[/]'),
                    '\n',
                    Align.center(grid),
                ),
                vertical='middle',
            ),
            style='cyan',
        )

    def on_key(self, key: events.Key) -> None:
        if key.key == 'j':
            if self.selected == len(self.channels) - 1:
                self.selected = 0
            else:
                self.selected += 1
        elif key.key == 'k':
            if self.selected == 0:
                self.selected = len(self.channels) - 1
            else:
                self.selected -= 1
        else:
            pass


class Messages(Widget):
    """Messages widget"""

    def __init__(self, messages: list[dict]) -> None:
        super().__init__()
        self.messages = messages

    messages = Reactive([])

    def render(self) -> Panel:
        grid = Table.grid(padding=(0, 1))
        grid.add_column(justify='right')
        grid.add_column()
        for message in self.messages:
            timestamp = datetime.strptime(
                message["createdAt"], '%Y-%m-%dT%H:%M:%S.%f'
            )
            grid.add_row(
                f'[bold white]{message["User"]["email"]} [magenta][{timestamp.strftime("%Y-%m-%d, %H:%M:%S")}][/magenta]:[/]',
                f'{message["text"]}',
            )
        return Panel(
            Align.center(
                grid,
                vertical='bottom',
            ),
            style='cyan',
        )


class ChatApp(App):
    """Main app class"""

    def on_cycle(self, selected: int):
        channel_id = self.my_channels[self.channels_view.selected]['id']
        self.messages_view.messages = self.client.get_messages(channel_id)

    async def on_load(self, event: events.Load) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        self.client = Client(
            email=settings.email, password=settings.password.get_secret_value()
        )
        self.channels = self.client.get_all_channels()
        self.my_channels = self.client.get_my_channels()
        self.messages = self.client.get_messages(channel_id=2)
        # await self.bind('tab', 'on_cycle', 'Cycle channels')
        await self.bind('ctrl+c', 'quit', show=False)
        await self.bind('b', 'view.toggle("sidebar")', 'Toggle sidebar')
        await self.bind('q', 'quit', 'Quit')

    async def on_mount(self, event: events.Mount) -> None:
        """Create and dock the widgets."""

        self.channels_view = Channels(channels=self.my_channels)
        channel_id = self.my_channels[self.channels_view.selected]['id']
        self.messages_view = Messages(
            messages=self.client.get_messages(channel_id=channel_id)
        )
        watch(self.channels_view, 'selected', self.on_cycle)
        await self.view.dock(Header(self.client.email), edge='top')
        await self.view.dock(Footer(), edge='bottom')
        await self.view.dock(
            self.channels_view,
            edge='left',
            size=30,
            name='sidebar',
        )
        await self.view.dock(self.messages_view, edge='right')


if __name__ == '__main__':
    ChatApp.run(title='Chat client')
