"""
UDP networking service for the Laser Tag system.

Responsibilities:
- Broadcast equipment IDs on UDP port 7500
- Receive tag events on UDP port 7501
- Support configurable network address
- Dispatch parsed messages to a registered callback
"""

import socket
import threading
from typing import Callable, Optional, Tuple, Union

from config import UDP_BROADCAST_ADDRESS, UDP_BROADCAST_PORT, UDP_RECEIVE_PORT

_send_sock: Optional[socket.socket] = None
_recv_sock: Optional[socket.socket] = None

_broadcast_address: str = UDP_BROADCAST_ADDRESS

_listener_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()

# Parsed message types:
# - ("tag", shooter_id, target_id) for "int:int"
# - ("code", code_int) for "int"
ParsedMsg = Union[Tuple[str, int, int], Tuple[str, int]]

_message_handler: Optional[Callable[[ParsedMsg], None]] = None


def start() -> None:
    """
    Initialize UDP sockets and start the receive listener.
    This function should be called once when the application starts.
    """

    global _send_sock, _recv_sock, _listener_thread

    if _send_sock is None:
        _send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if _recv_sock is None:
        _recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _recv_sock.bind(("0.0.0.0", UDP_RECEIVE_PORT))
        _recv_sock.settimeout(0.5)

    if _listener_thread is None or not _listener_thread.is_alive():
        _stop_event.clear()
        _listener_thread = threading.Thread(target=_listen_loop, daemon=True)
        _listener_thread.start()


def stop() -> None:
    """
    Stop the receive listener and close sockets.
    Safe to call on app shutdown.
    """

    global _send_sock, _recv_sock

    _stop_event.set()

    if _recv_sock is not None:
        try:
            _recv_sock.close()
        except OSError:
            pass
        _recv_sock = None

    if _send_sock is not None:
        try:
            _send_sock.close()
        except OSError:
            pass
        _send_sock = None


def get_broadcast_address() -> str:
    """Return the current UDP broadcast address."""
    return _broadcast_address


def set_broadcast_address(address: str) -> None:
    """
    Update the network address used for UDP broadcasts.
    """

    global _broadcast_address
    _broadcast_address = address.strip()


def set_message_handler(handler: Optional[Callable[[ParsedMsg], None]]) -> None:
    """
    Register a callback that receives parsed UDP messages.
    """
    global _message_handler
    _message_handler = handler


def send_message(value: int) -> None:
    """
    Broadcast a single integer message over UDP.
    Used for equipment IDs, 202, 221, and gameplay reply packets.
    """

    if _send_sock is None:
        start()

    message = str(int(value)).encode("ascii")
    _send_sock.sendto(message, (_broadcast_address, UDP_BROADCAST_PORT))


def send_equipment_id(equipment_id: int) -> None:
    """
    Broadcast the given equipment ID over UDP.
    This is called after a player is assigned an equipment ID.
    """
    send_message(equipment_id)


def _listen_loop() -> None:
    """
    Background thread: listen for UDP on 7501 and dispatch parsed messages.
    """

    print(f"[UDP] Listening on 0.0.0.0:{UDP_RECEIVE_PORT}", flush=True)

    while not _stop_event.is_set():
        try:
            assert _recv_sock is not None
            data, addr = _recv_sock.recvfrom(4096)
        except socket.timeout:
            continue
        except OSError:
            break

        text = data.decode("ascii", errors="ignore").strip()
        parsed = _parse_message(text)

        if parsed is None:
            print(f"[UDP] From {addr}: Unrecognized payload {data!r}", flush=True)
            continue

        print(f"[UDP] From {addr}: {parsed}", flush=True)

        if _message_handler is not None:
            try:
                _message_handler(parsed)
            except Exception as error:
                print(f"[UDP] Handler error: {error}", flush=True)


def _parse_message(text: str) -> Optional[ParsedMsg]:
    """
    Parse either:
    - "int:int" -> ("tag", shooter, target)
    - "int"     -> ("code", code)
    """

    if not text:
        return None

    if ":" in text:
        parts = text.split(":")
        if len(parts) != 2:
            return None

        try:
            shooter = int(parts[0].strip())
            target = int(parts[1].strip())
            return ("tag", shooter, target)
        except ValueError:
            return None

    try:
        code = int(text)
        return ("code", code)
    except ValueError:
        return None