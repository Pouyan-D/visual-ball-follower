import cv2
import numpy as np

from ball_follower.vision import detect_orange_ball


def _blank():
    return np.zeros((240, 320, 3), dtype=np.uint8)


def test_detects_large_orange_circle():
    image = _blank()
    cv2.circle(image, (94, 117), 25, (0, 140, 255), -1)
    ball = detect_orange_ball(image)
    assert ball is not None
    assert abs(ball.center_x - 94) <= 1
    assert abs(ball.center_y - 117) <= 1
    assert ball.circularity > 0.6


def test_does_not_detect_empty_image():
    assert detect_orange_ball(_blank()) is None


def test_rejects_non_orange_circle():
    image = _blank()
    cv2.circle(image, (94, 117), 25, (255, 0, 0), -1)
    assert detect_orange_ball(image) is None


def test_rejects_small_orange_dot():
    image = _blank()
    cv2.circle(image, (94, 117), 8, (0, 140, 255), -1)
    assert detect_orange_ball(image) is None


def test_selects_largest_valid_orange_circle():
    image = _blank()
    cv2.circle(image, (75, 95), 19, (0, 140, 255), -1)
    cv2.circle(image, (240, 130), 30, (0, 140, 255), -1)
    ball = detect_orange_ball(image)
    assert ball is not None
    assert abs(ball.center_x - 240) <= 1


def test_rejects_invalid_frame():
    try:
        detect_orange_ball(np.zeros((10, 10), dtype=np.uint8))
    except ValueError:
        return
    raise AssertionError('Expected ValueError for grayscale frame')
