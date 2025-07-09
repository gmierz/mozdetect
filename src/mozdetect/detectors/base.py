# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class DetectorRegistry:
    _detectors = {}

    @staticmethod
    def add(detector_class, detector_name):
        """Add a detector to the registry of detectors.

        Detectors added to the registry will become available through the `get_detectors`
        method using the provided `detector_name`.

        :param str detector_name: Name of the detector.
        """
        DetectorRegistry._detectors[detector_name] = detector_class

    @staticmethod
    def get_detectors():
        """Return all the detectors that were gathered."""
        return DetectorRegistry._detectors


class BaseDetector:
    """Base class for all group detectors."""

    def __init_subclass__(cls, detector_name, **kwargs):
        super().__init_subclass__(**kwargs)
        DetectorRegistry.add(cls, detector_name)

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
