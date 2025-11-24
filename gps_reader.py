import serial
import pynmea2
import time


class GPSReader:
    def __init__(self, port="/dev/ttyUSB0", baud=9600):
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
        except Exception:
            self.ser = None

    def get_current_position(self, timeout: float = 2.0):
        """
        Returns:
            (lat, lon, speed_knots, course_deg)
            OR None if no GPS fix or timeout
        """

        if self.ser is None:
            return None

        start = time.time()
        lat = lon = speed = course = None

        while time.time() - start < timeout:
            try:
                line = self.ser.readline().decode("ascii", errors="replace").strip()

                # Parse GPGGA for coordinates + fix
                if line.startswith("$GPGGA"):
                    msg = pynmea2.parse(line)

                    # If GPS has no fix, skip
                    if msg.gps_qual == 0:  # 0 = invalid fix
                        continue

                    lat = msg.latitude
                    lon = msg.longitude

                # Parse GPRMC for speed + heading
                elif line.startswith("$GPRMC"):
                    msg = pynmea2.parse(line)
                    speed = getattr(msg, "spd_over_ground", 0) or 0
                    course = getattr(msg, "true_course", 0) or 0

                # If we got at least valid lat/lon, return
                if lat is not None and lon is not None:
                    return lat, lon, speed or 0, course or 0

            except Exception:
                continue

        # Timeout → no fix
        return None
