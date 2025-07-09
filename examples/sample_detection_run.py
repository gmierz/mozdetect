import mozdetect

from mozdetect.telemetry_query import get_metric_table

ts_detectors = mozdetect.get_timeseries_detectors()
cdf_ts_detector = ts_detectors["cdf_squared"]

print("Querying for data...")
data = get_metric_table("network_tls_handshake", "Windows", process="content", use_fog=True)
timeseries = mozdetect.TelemetryTimeSeries(data)

print("Running detections...")
ts_detector = cdf_ts_detector(timeseries)
detections = ts_detector.detect_changes()

for detection in detections:
    print(detection)
