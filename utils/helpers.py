import logging

# Initialize a simple logger
logging.basicConfig(level=logging.INFO)

def log(message: str):
    """
    Prints a log message with INFO level.
    Used in startup and other debugging prints.
    """
    logging.info(message)


def get_relative_position(bbox: tuple, frame_width: int) -> str:
    """
    Determines whether an object lies to the left, right,
    or center of the camera frame.

    Even though obstacle haptics are now center-only,
    this is still used for navigation turn instructions.
    """
    x1, _, x2, _ = bbox

    center_x = (x1 + x2) / 2   # middle of the object in X-axis

    if center_x < frame_width / 3:
        return "left"
    elif center_x > 2 * frame_width / 3:
        return "right"
    return "center"
