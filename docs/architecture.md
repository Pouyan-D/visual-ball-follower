# Architecture and engineering decisions

## Pipeline

`/camera/image_raw` (`sensor_msgs/Image`) → `cv_bridge` → BGR-to-HSV conversion → orange mask → erosion/dilation → contour validation → center-pixel error → proportional steering → `/cmd_vel` (`geometry_msgs/Twist`).

## Notes

- Original experimental segmentation values carried forward: HSV `[6,110,110]` to `[25,255,255]`; erosion/dilation 3 iterations; `area > 400`, `radius > 15`, `circularity > 0.6`.
- Steering gain originally used: `Kp_angular = 0.004`, maximum angular speed `1.0 rad/s`.
- `linear_speed = 0.08 m/s` is **a new conservative example**, not independently verified as the original value.
- Motion is opt-in and guarded by an image freshness timeout; there is no obstacle detector or distance controller.
- Detection relies on orange color in HSV, so background colors and illumination affect false positives and recall.
- Future engineering work: add annotated demo footage and failure cases, compare tracking vs. color thresholding, publish an optional debug image, and measure processing latency / command throughput.

## What is and isn't tested

Pure-OpenCV detector logic has synthetic-image unit tests. Actual camera integration, camera QoS behavior, real TurtleBot3 steering sign and real robot safety have not been verified in this reconstructed package.
