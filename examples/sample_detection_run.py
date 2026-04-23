import mozdetect

from mozdetect.telemetry_query import get_metric_labels, get_metric_table

PROBE = "perf_dns_first_byte"
OS = "Windows"
FROM_BUILD_DATE = "2025-09-13"
LABELED = True

ts_detectors = mozdetect.get_timeseries_detectors()
cdf_ts_detector = ts_detectors["cdf_squared"]


def run_detection(label=None):
    data = get_metric_table(
        PROBE,
        OS,
        use_fog=True,
        from_build_date=FROM_BUILD_DATE,
        label=label,
    )
    timeseries = mozdetect.TelemetryTimeSeries(data)
    ts_detector = cdf_ts_detector(timeseries)
    return ts_detector.detect_changes()


if LABELED:
    print("Querying for labels...")
    labels = get_metric_labels(PROBE, OS)
    print(f"Found {len(labels)} labels: {labels}")

    for label in labels:
        print(f"\nRunning detections for label: {label}")
        detections = run_detection(label=label)
        for detection in detections:
            print(f"  {detection.location}")
else:
    print("Querying for data...")
    detections = run_detection()
    print("Running detections...")
    for detection in detections:
        print(detection.location)
