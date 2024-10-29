# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class BaseDetector:
    """Base class for all group detectors."""

    def __init__(self, groups=None, **kwargs):
        """Initialize the detector.

        :param list groups: A list of DataFrame objects to compare between.
            Generally expected for there to be TWO groups to compare, but it's
            possible to have multiple to do a cross-comparison (assuming the
            detector supports this).
        """
        self.groups = groups

    def _coalesce_groups(self, groups):
        """Used to determine the groups to compare.

        The groups passed as an argument have a higher priority than the groups
        used to initialize the detector.

        :param list groups: A list of groups to compare or None.
        :return list: The groups that should be compared.
        """
        if not groups:
            if not self.groups:
                raise ValueError("Groups to compare have not been specified.")
            return self.groups
        return groups

    def detect_changes(self, groups=None, **kwargs):
        """Detect changes between two groups of data points.

        :param list groups: A list of the groups to compare.
        """
        pass
