# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class Detection:
    """Used to represent a change detection in a timeseries."""

    def __init__(self, previous_value, new_value, confidence, location, direction):
        """Create a new detected change.

        :param float previous_value: The previous value before the detected change.
        :param float new_value: The new value at the detected change location.
        :param float confidence: The confidence of the detected change.
        :param str location: The location of the detected change. Can be a revision,
            build_id, or something else that represents the place at which a regression
            was detected.
        """
        self.previous_value = previous_value
        self.new_value = new_value
        self.confidence = confidence
        self.location = location
        self.direction = direction

    def __repr__(self):
        return (
            f"Detection<"
            f"previous_value={self.previous_value}, new_value={self.new_value}, "
            f"confidence={self.confidence}, location={self.location}, "
            f"direction={self.direction}>"
        )
