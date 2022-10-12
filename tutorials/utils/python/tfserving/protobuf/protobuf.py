from . import messages
from . import output

from .output import get_message_file_formats
from .messages import get_message_types

def generate_message_file(
        msg: str,
        args: dict = {},
        out_format: str = None,
        out_file: str = None
):
    gen_message = messages.get_message_gen(msg)
    if gen_message is None:
        print("ERROR: message type not found")
        return

    message = gen_message(args=args)

    output.gen_output_file(message, out_format, out_file)