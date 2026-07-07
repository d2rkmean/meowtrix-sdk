# meowtrix-sdk
 
An elegant, async-first Python library designed for writing Matrix bots with built-in end-to-end encryption (E2EE) support.
 
> [!WARNING]
> **Development Status:** This project is currently in the conceptual development stage (Alpha). The API is unstable, experimental, and subject to breaking changes. It is not yet recommended for production use.
 
## Features
 
- **AsyncIO First:** Built on top of `httpx` and `asyncio` for maximum performance.
- **Smart Persistence:** Context-aware session management using `aiosqlite`.
- **Cryptographic Foundation:** Planned robust E2EE powered by `vodozemac` (Olm/Megolm).
- **Modern Tooling:** Zero-compromise code quality enforced by `ruff` and strict `mypy` type checking.
## Installation
 
Since the library is under active development, you can clone the repository and install it in editable mode using `hatch` or `pip`:
 
```bash
git clone https://github.com/d2rkmean/meowtrix-sdk.git
cd meowtrix-sdk
pip install -e .
```
 
## Quick Start (Concept)
 

```python
import asyncio
from meowtrix.sdk.listener import Listener
from meowtrix.sdk.bot import Bot
from meowtrix.sdk.events import TextMessage, Message
 
listener = Listener()
bot = Bot(homeserver="matrix.org", login="example", password="example")
 
listener.add_bot(bot)
 
@listener.on_event(TextMessage, filter=None)
async def handle_message(event: Message) -> None:
    await event.reply(Message(text="pong!"))
 
if __name__ == "__main__":
    asyncio.run(listener.start_polling())
```

## Development
 
We use `hatchling` as the build backend and `ruff` for code quality checks.
 
### Prerequisites
 
Make sure you have Python 3.11+ installed. For local development, it's recommended to use a virtual environment with development dependencies installed:
 
```bash
pip install -e ".[dev]"
```
 
### Makefile Automation
 
The project provides a few simple `make` commands to keep the codebase perfectly clean:
 
| Command | Description |
|---|---|
| `make format` | Format code |
| `make lint` | Lint and auto-fix rules |
| `make mypy` | Run strict type checking |
| `make all` | Run all checks at once (Format, Lint, MyPy) |
 
## License
 
This project is licensed under the LGPL-2.1 License - see the [LICENSE](LICENSE) file for details.
 
