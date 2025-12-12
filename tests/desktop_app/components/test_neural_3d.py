import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import math
import numpy as np
import pytest

# Force mock mode (must be before mock_qt import)

# Patch modules BEFORE importing the code under test
from tests.desktop_app.mock_qt import mock_qt_modules

modules = mock_qt_modules()
for name, mod in modules.items():
    sys.modules[name] = mod

# Mark tests to run in forked subprocess
pytestmark = pytest.mark.forked

# Now import
from desktop_app.components.neural_3d import NeuralNetwork3D

class TestNeuralNetwork3D(unittest.TestCase):
    def setUp(self):
        # Configure QPixmap/QImage mocks to return integers for width/height
        # because the code does math on them
        img_mock = modules['PyQt6.QtGui'].QImage.return_value
        img_mock.width.return_value = 32
        img_mock.height.return_value = 32

        pixmap_mock = modules['PyQt6.QtGui'].QPixmap.fromImage.return_value
        pixmap_mock.width.return_value = 32
        pixmap_mock.height.return_value = 32

        # Also ensure QPixmap() constructor returns something with width/height if called directly
        # The code uses QPixmap.fromImage(img)

    def test_initialization(self):
        nn = NeuralNetwork3D(num_nodes=50)
        self.assertEqual(len(nn.points), 50)
        self.assertEqual(nn.points.shape, (50, 3))
        self.assertEqual(len(nn.velocities), 50)
        self.assertEqual(len(nn.phases), 50)

        # Check assets generation
        # S5906: Use assertGreater
        self.assertGreater(len(nn.star_textures), 0)

    def test_update_logic(self):
        nn = NeuralNetwork3D(num_nodes=10)
        original_points = np.copy(nn.points)
        original_rot_x = nn.rot_x
        original_rot_y = nn.rot_y

        # Simulate Mouse Movement (Update Rotation)
        nn.update(0.5, -0.5)

        # Rotation should change
        self.assertNotEqual(nn.rot_x, original_rot_x)
        self.assertNotEqual(nn.rot_y, original_rot_y)

        # Points should move (velocity)
        self.assertFalse(np.array_equal(nn.points, original_points))

        # Phases should update
        # We can't easily check exact values without mocking random, but they should change

    def test_pulse_spawning(self):
        nn = NeuralNetwork3D(num_nodes=5)
        # Manually seed connections
        nn.connections = [(0, 1, 100.0)]

        # Force a spawn (random might fail, so we patch random)
        with patch('random.random', return_value=0.01): # < 0.15
            with patch('random.choice', return_value=(0, 1, 100.0)):
                nn.update(0, 0)

        # S5906: Use assertGreater
        self.assertGreater(len(nn.pulses), 0)
        self.assertEqual(nn.pulses[0][0], 0) # Start idx
        self.assertEqual(nn.pulses[0][1], 1) # End idx

    def test_project_and_render(self):
        nn = NeuralNetwork3D(num_nodes=10)
        painter = MagicMock()
        width = 800
        height = 600

        # Run projection
        nn.project_and_render(painter, width, height)

        # Check that painter drew something
        # Note: Background fill is done in the View, not the Component.

        # 1. Nodes (Pixmaps)
        # Should be called 10 times
        self.assertTrue(painter.drawPixmap.called)
        self.assertEqual(painter.drawPixmap.call_count, 10) # 10 nodes

        # 2. Lines (Connections)
        # Force points close to ensure connections
        nn.points = np.zeros((10, 3)) # All at 0,0,0
        # Reset mock
        painter.reset_mock()
        nn.project_and_render(painter, width, height)

        # Should draw lines now (all connected to all others roughly)
        self.assertTrue(painter.drawLine.called)

if __name__ == '__main__':
    unittest.main()
