# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging
import numpy as np
import pandas
import base64
from io import BytesIO

from matplotlib import pyplot as plt

from datetime import timedelta
from prettytable import PrettyTable
from scipy.signal import find_peaks

from mozdetect.detectors import CDFSquaredDetector
from mozdetect.timeseries_detectors.base import BaseTimeSeriesDetector
from mozdetect.timeseries_detectors.detection import Detection
from mozdetect.utils import lowpass_filter

logger = logging.getLogger("CDFSquaredTimeSeries")


class CDFSquaredTimeSeriesDetector(BaseTimeSeriesDetector, timeseries_detector_name="cdf_squared"):
    """Analyzes a time series of histograms using CDFs to detect changes."""

    def __init__(self, timeseries, start_date=None, end_date=None, **kwargs):
        super().__init__(timeseries, **kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def _coalesce_dates(self, start_date, end_date):
        return (
            self.start_date or start_date,
            self.end_date or end_date,
        )

    def _calculate_differences(self):
        """Calculates all the CDF differences across the full time series."""
        detector = CDFSquaredDetector()

        start_date, end_date = self._coalesce_dates(
            self.timeseries.cumulative_multiday_histograms["date"].min(),
            self.timeseries.cumulative_multiday_histograms["date"].max(),
        )

        current_date = start_date
        differences = pandas.DataFrame()
        while current_date <= end_date - timedelta(days=7):
            current_date_hist = self.timeseries.cumulative_multiday_histograms[
                self.timeseries.cumulative_multiday_histograms["date"] == current_date
            ][["bin", "cdf"]]
            next_date_hist = self.timeseries.cumulative_multiday_histograms[
                self.timeseries.cumulative_multiday_histograms["date"]
                == current_date + timedelta(days=7)
            ][["bin", "cdf"]]

            difference = detector.detect_changes(groups=[current_date_hist, next_date_hist])
            difference["date"] = [current_date + timedelta(days=6)]
            differences = pandas.concat(
                [differences, pandas.DataFrame(difference)], ignore_index=True
            )

            current_date += timedelta(days=1)

        logger.debug(differences)
        differences["filtered_sq_diff"] = lowpass_filter(differences["sq_diff"], 20, 100)

        return differences

    def _find_alerts(self, differences, alert_threshold=0.85):
        start_date, end_date = self._coalesce_dates(
            differences["date"].min(), differences["date"].max()
        )

        threshold = abs(differences["filtered_sq_diff"]).quantile(alert_threshold)

        peaks, _ = find_peaks(differences["filtered_sq_diff"], height=threshold, distance=3)
        valleys, _ = find_peaks(-differences["filtered_sq_diff"], height=threshold, distance=3)

        df_peaks = pandas.DataFrame({"date": differences.loc[peaks, "date"], "direction": "up"})
        df_valleys = pandas.DataFrame(
            {"date": differences.loc[valleys, "date"], "direction": "down"}
        )

        detections = (
            pandas.concat([df_peaks, df_valleys]).sort_values("date").reset_index(drop=True)
        )

        return detections

    def _get_interpolated_percentile(self, histogram, percentile):
        """Get an interpolated percentile value from the given histogram.

        :param pandas.DataFrame histogram: The histogram to get an interpolated
            percentile value from.
        :param float percentile:  The percentile to obtain a value for.
        """
        bucket_before = histogram[histogram["cdf"] <= percentile].max()
        bucket = histogram[histogram["cdf"] > percentile].min()
        bucket_after = histogram[histogram["cdf"] > percentile].iloc[1]

        x = np.array([bucket_before["cdf"], bucket["cdf"]])
        y = np.array([bucket["bin"], bucket_after["bin"]])
        return np.interp(percentile, x, y)

    def _describe_detection(self, detection):
        """Produce information about the detection."""
        if self.timeseries.cumulative_multiday_histograms is None:
            raise ValueError(
                "Cannot produce a description of the detection without a multiday average."
            )

        before_histogram = self.timeseries.cumulative_multiday_histograms[
            self.timeseries.cumulative_multiday_histograms["date"]
            == detection["date"] - timedelta(days=7)
        ]
        after_histogram = self.timeseries.cumulative_multiday_histograms[
            self.timeseries.cumulative_multiday_histograms["date"] == detection["date"]
        ]

        merged_hist = pandas.merge(
            before_histogram, after_histogram, on="bin", suffixes=("_current", "_next")
        )
        merged_hist["diff"] = merged_hist["cdf_current"] - merged_hist["cdf_next"]
        total_diff = merged_hist["diff"].sum()

        detection_info = []
        detection_info.append(
            [
                "Total Samples",
                before_histogram["count"].sum(),
                after_histogram["count"].sum(),
            ]
        )
        detection_info.append(
            [
                "Interpolated Median",
                self._get_interpolated_percentile(before_histogram, 0.5),
                self._get_interpolated_percentile(after_histogram, 0.5),
            ]
        )
        detection_info.append(
            [
                "Interpolated p05",
                self._get_interpolated_percentile(before_histogram, 0.05),
                self._get_interpolated_percentile(after_histogram, 0.05),
            ]
        )
        detection_info.append(
            [
                "Interpolated p95",
                self._get_interpolated_percentile(before_histogram, 0.95),
                self._get_interpolated_percentile(after_histogram, 0.95),
            ]
        )
        detection_info.append(["CDF Diff", "", total_diff])
        detection_info.append(
            [
                "CDF Shift",
                "",
                "Left" if total_diff < -0.05 else "Right" if total_diff > 0.05 else "Mixed",
            ]
        )

        table = PrettyTable()
        table.field_names = ["Metric", "Before", "After"]
        table.add_rows(detection_info)

        logger.debug("Alert Generated: " + detection["date"].strftime("%Y-%m-%d"))
        logger.debug(table)

        detection_dict = {d[0]: d[1:] for d in detection_info}

        # Store data representing the data before and after the detection
        detection_dict["additional_data"] = {
            "before": before_histogram[["bin", "cdf", "count"]].to_dict(orient="list"),
            "after": after_histogram[["bin", "cdf", "count"]].to_dict(orient="list"),
        }

        # Generate plot and add to detection info attachments
        detection_dict["attachments"] = []
        try:
            plot_image = self._plot_detection(
                detection["date"], before_histogram, after_histogram, detection["direction"]
            )
            detection_dict["attachments"].append(
                {
                    "data": plot_image,
                    "content_type": "image/png",
                    "file_name": f"cdf_difference_{detection['date']}.png",
                    "summary": (
                        "Graph showing the CDF difference between before and after the detection."
                    ),
                }
            )
        except Exception as e:
            logger.info(f"Failed to generate detection plot: {e}")

        return detection_dict

    def _plot_detection(self, detection_date, before_histogram, after_histogram, direction):
        """Create a graph showing the CDF before and after the detection.

        :param datetime detection_date: The date of the detection.
        :param DataFrame before_histogram: Histogram data before the detection.
        :param DataFrame after_histogram: Histogram data after the detection.
        :param str direction: The direction of the detection (up/down).
        :return str: Base64-encoded PNG image string.
        """
        # Create the plot
        plt.figure(figsize=(12, 6))

        # Plot both CDFs
        plt.plot(
            before_histogram["bin"],
            before_histogram["cdf"],
            label="Before",
            linewidth=2,
            color="blue",
        )
        plt.plot(
            after_histogram["bin"],
            after_histogram["cdf"],
            label="After",
            linewidth=2,
            color="red",
        )

        # Find the maximum bin value where CDF <= 0.99 for both histograms
        max_bin_before = before_histogram[before_histogram["cdf"] <= 0.99]["bin"].max()
        max_bin_after = after_histogram[after_histogram["cdf"] <= 0.99]["bin"].max()
        max_bin = max(max_bin_before, max_bin_after)
        if not pandas.isna(max_bin):
            plt.xlim(left=0, right=max_bin)

        # Add labels and title
        plt.xlabel("Bin", fontsize=12)
        plt.ylabel("Cumulative Distribution (CDF)", fontsize=12)
        plt.title(
            f"CDF Comparison: Detection on {detection_date.strftime('%Y-%m-%d')} "
            f"(Direction: {direction})",
            fontsize=14,
            fontweight="bold",
        )
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)

        # Save to BytesIO buffer and encode as base64
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
        plt.close()
        return img_str

    def detect_changes(self, multiday_average_days=7, alert_threshold=0.85, **kwargs):
        """Detects changes in a telemetry probe using the CDF squared detection method.

        :param int multiday_average_days: The number of days to use in the multiday average.

        :return list: A list of Detection objects representing where a detection occurred.
        """
        self.timeseries.get_cumulative_by_day(start_date=self.start_date, end_date=self.end_date)
        self.timeseries.get_multiday_average(days=multiday_average_days)

        differences = self._calculate_differences()
        pre_detections = self._find_alerts(differences, alert_threshold=alert_threshold)

        detections = []
        for i in range(len(pre_detections)):
            detection = pre_detections.iloc[i]
            detection_info = self._describe_detection(detection)

            detections.append(
                Detection(
                    detection_info["Total Samples"][0],
                    detection_info["Total Samples"][1],
                    detection_info["CDF Diff"][1],
                    detection["date"],
                    detection["direction"],
                    **detection_info,
                )
            )

        return detections
