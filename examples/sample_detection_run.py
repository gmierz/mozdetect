import mozdetect

from mozdetect.telemetry_query import get_metric_table

ts_detectors = mozdetect.get_timeseries_detectors()
cdf_ts_detector = ts_detectors["cdf_squared"]

# Set from_build_date="2025-09-13" on get_metric_table or something similar to look
# from a specific date

print("Querying for data...")
data = get_metric_table(
    "network_tls_handshake",
    "Windows",
    process="content",
    use_fog=True,
    from_build_date="2025-09-13",
)
timeseries = mozdetect.TelemetryTimeSeries(data)

print("Running detections...")
ts_detector = cdf_ts_detector(timeseries)
detections = ts_detector.detect_changes()

for detection in detections:
    print(detection.location)
