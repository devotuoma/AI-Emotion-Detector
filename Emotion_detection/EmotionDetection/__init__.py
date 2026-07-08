"""
EmotionDetection package.

This package exposes the `emotion_detector` function used by both unit tests
and the Flask web service.
"""

from .emotion_detection import emotion_detector

__all__ = ["emotion_detector"]

