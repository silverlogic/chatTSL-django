from model_utils import Choices

INPUT_EVENT_TYPE = Choices(
    ("PING", "ping", "ping"),
    ("create_message", "create_message", "create_message"),
)

OUTPUT_EVENT_TYPE = Choices(
    ("PONG", "pong", "pong"),
    ("on_message_created", "on_message_created", "on_message_created"),
    ("on_error", "on_error", "on_error"),
)
