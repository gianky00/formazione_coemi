import math
import random
import numpy as np
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QRadialGradient, QPixmap, QPainter, QBrush, QImage

class NeuralNetwork3D:
    def __init__(self, num_nodes=100, connect_distance=200):
        # Reduced default nodes to 100 for better performance ("scatta" fix)
        self.num_nodes = num_nodes
        self.connect_distance_sq = connect_distance ** 2

        # --- 3D State (Vectorized) ---
        # Position X, Y, Z centered at 0,0,0
        # Range approx -800 to 800
        self.points = (np.random.rand(num_nodes, 3) - 0.5) * 1600

        # Velocity vector (slow drift)
        self.velocities = (np.random.rand(num_nodes, 3) - 0.5) * 1.5

        # Phase for "breathing" effect (0 to 2pi)
        self.phases = np.random.rand(num_nodes) * 2 * math.pi
        self.phase_speeds = np.random.rand(num_nodes) * 0.05 + 0.02

        # Current Rotation (Euler angles)
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.target_rot_x = 0.0
        self.target_rot_y = 0.0

        # --- Pulse System ---
        self.pulses = []
        self.connections = [] # Cached connections [(i, j, dist_sq)]

        # --- Pre-calculated Assets ---
        self.star_textures = self._generate_star_textures()

    def _generate_star_textures(self):
        """Pre-renders glowing star textures at different sizes to avoid QGradient cost."""
        textures = {}
        sizes = [8, 16, 32, 64, 128] # Pixel diameters
        base_color = QColor(100, 200, 255) # Cyan-ish Blue

        for size in sizes:
            img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
            img.fill(0)

            painter = QPainter(img)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Radial Gradient from center
            grad = QRadialGradient(size/2, size/2, size/2)
            c_center = QColor(base_color)
            c_center.setAlpha(255)
            c_edge = QColor(base_color)
            c_edge.setAlpha(0)

            grad.setColorAt(0.0, c_center)
            grad.setColorAt(0.4, c_center) # Core
            grad.setColorAt(1.0, c_edge)   # Glow

            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()

            textures[size] = QPixmap.fromImage(img)

        return textures

    def update(self, mouse_norm_x, mouse_norm_y):
        """
        Updates the simulation.
        mouse_norm_x/y: -1.0 to 1.0 (screen center is 0,0)
        """
        # 1. Update Rotation Target (Smooth Camera)
        self.target_rot_y = mouse_norm_x * 0.5 # Yaw
        self.target_rot_x = -mouse_norm_y * 0.5 # Pitch

        # Lerp rotation
        lerp_speed = 0.05
        self.rot_x += (self.target_rot_x - self.rot_x) * lerp_speed
        self.rot_y += (self.target_rot_y - self.rot_y) * lerp_speed

        # 2. Update Positions (Drift)
        self.points += self.velocities

        # Wrap around boundary
        limit = 1000

        # Safe Axis Checks (Fixes IndexError)
        mask_x_high = self.points[:, 0] > limit
        mask_x_low = self.points[:, 0] < -limit
        self.velocities[mask_x_high, 0] *= -1
        self.velocities[mask_x_low, 0] *= -1

        mask_y_high = self.points[:, 1] > limit
        mask_y_low = self.points[:, 1] < -limit
        self.velocities[mask_y_high, 1] *= -1
        self.velocities[mask_y_low, 1] *= -1

        mask_z_high = self.points[:, 2] > limit
        mask_z_low = self.points[:, 2] < -limit
        self.velocities[mask_z_high, 2] *= -1
        self.velocities[mask_z_low, 2] *= -1

        # Clamp positions
        np.clip(self.points, -limit, limit, out=self.points)

        # 3. Update Breathing Phases
        self.phases += self.phase_speeds

        # 4. Update Pulses
        active_pulses = []
        for p in self.pulses:
            p[2] += p[3] # Progress += Speed
            if p[2] < 1.0:
                active_pulses.append(p)
        self.pulses = active_pulses

        # Randomly spawn new pulses
        if self.connections and random.random() < 0.15:
            conn = random.choice(self.connections)
            speed = random.uniform(0.02, 0.05)
            self.pulses.append([conn[0], conn[1], 0.0, speed])


    def project_and_render(self, painter, width, height):
        center_x = width / 2
        center_y = height / 2
        focal_length = 800

        # --- 1. Rotation Matrices ---
        cx, sx = math.cos(self.rot_x), math.sin(self.rot_x)
        cy, sy = math.cos(self.rot_y), math.sin(self.rot_y)

        # Rotate around Y axis
        x = self.points[:, 0]
        y = self.points[:, 1]
        z = self.points[:, 2]

        x_rot_y = x * cy - z * sy
        z_rot_y = x * sy + z * cy

        # Rotate around X axis
        y_final = y * cx - z_rot_y * sx
        z_final = y * sx + z_rot_y * cx
        x_final = x_rot_y

        # --- 2. Perspective Projection ---
        z_safe = z_final + 1200
        scale = focal_length / np.maximum(z_safe, 0.1)

        x_2d = x_final * scale + center_x
        y_2d = y_final * scale + center_y

        # --- 3. Draw Connections & Pulses ---
        self.connections = []
        painter.setPen(QColor(100, 200, 255, 40))

        pos_3d = np.column_stack((x_final, y_final, z_final))
        diff = pos_3d[:, np.newaxis, :] - pos_3d[np.newaxis, :, :]
        dists_sq = np.sum(diff**2, axis=-1)

        mask = np.triu(dists_sq < self.connect_distance_sq, k=1)
        rows, cols = np.nonzero(mask)

        # Draw Lines
        for i, j in zip(rows, cols):
            p1 = QPointF(x_2d[i], y_2d[i])
            p2 = QPointF(x_2d[j], y_2d[j])

            d_sq = dists_sq[i, j]
            alpha = int(255 * (1.0 - (d_sq / self.connect_distance_sq)))
            if alpha > 0:
                self.connections.append((i, j, d_sq))
                color = QColor(147, 197, 253)
                color.setAlpha(max(0, min(80, int(alpha * 0.3))))
                painter.setPen(color)
                painter.drawLine(p1, p2)

        # Draw Pulses
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.pulses:
            start_idx, end_idx, progress, _ = p
            sx, sy = x_2d[start_idx], y_2d[start_idx]
            ex, ey = x_2d[end_idx], y_2d[end_idx]

            curr_x = sx + (ex - sx) * progress
            curr_y = sy + (ey - sy) * progress

            size = 16
            tex_key = 16
            tex = self.star_textures[tex_key]

            painter.setOpacity(0.8)
            painter.drawPixmap(int(curr_x - size/2), int(curr_y - size/2), tex)
            painter.setOpacity(1.0)

        # --- 4. Draw Nodes (Z-Sorted) ---
        sort_indices = np.argsort(z_safe)[::-1]

        for i in sort_indices:
            s = scale[i]
            base_size = scale[i] * 10
            breath = 1.0 + math.sin(self.phases[i]) * 0.2
            final_size = base_size * breath

            if final_size < 12: tex_key = 16
            elif final_size < 24: tex_key = 32
            else: tex_key = 64
            if final_size >= 64: tex_key = 128

            if tex_key not in self.star_textures: tex_key = 64
            tex = self.star_textures[tex_key]

            x = x_2d[i] - (tex.width() / 2)
            y = y_2d[i] - (tex.height() / 2)

            depth_alpha = min(1.0, max(0.2, (scale[i] * 2.0)))
            painter.setOpacity(depth_alpha)
            painter.drawPixmap(int(x), int(y), tex)

        painter.setOpacity(1.0)
