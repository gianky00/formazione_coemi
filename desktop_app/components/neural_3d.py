import math
import random
import numpy as np
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QRadialGradient, QPixmap, QPainter, QBrush, QImage

class NeuralNetwork3D:
    def __init__(self, num_nodes=100, connect_distance=250):
        self.num_nodes = num_nodes
        self.connect_distance_sq = connect_distance ** 2

        # Use new Generator API
        self.rng = np.random.default_rng()

        # --- 3D State (Vectorized) ---
        # Position X, Y, Z centered at 0,0,0
        # Range approx -800 to 800
        self.points = (self.rng.random((num_nodes, 3)) - 0.5) * 1600

        # Velocity vector (slow drift)
        self.velocities = (self.rng.random((num_nodes, 3)) - 0.5) * 1.5

        # Phase for "breathing" effect (0 to 2pi)
        self.phases = self.rng.random(num_nodes) * 2 * math.pi
        self.phase_speeds = self.rng.random(num_nodes) * 0.05 + 0.02

        # Current Rotation (Euler angles)
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.target_rot_x = 0.0
        self.target_rot_y = 0.0

        # Warp Mode State
        self.warp_active = False
        self.warp_speed = 0.0

        # --- Pulse System ---
        # List of active pulses: [start_index, end_index, progress (0.0-1.0), speed]
        self.pulses = []
        self.connections = [] # Cached connections [(i, j, dist_sq)]

        # --- Pre-calculated Assets ---
        self.star_textures = self._generate_star_textures()

    def _generate_star_textures(self):
        """Pre-renders glowing star textures at different sizes to avoid QGradient cost."""
        textures = {}
        sizes = [8, 16, 32, 64] # Pixel diameters
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

    def reset(self):
        """Resets the engine to initial state (stops warp)."""
        self.warp_active = False
        self.warp_speed = 0.0
        # Reset positions to ensure we aren't stuck in a "tunnel"
        self.points = (self.rng.random((self.num_nodes, 3)) - 0.5) * 1600
        self.velocities = (self.rng.random((self.num_nodes, 3)) - 0.5) * 1.5

    def start_warp(self):
        """Activates the cinematic warp effect."""
        self.warp_active = True
        self.warp_speed = 5.0 # Starting speed

    def update(self, mouse_norm_x, mouse_norm_y):
        """
        Updates the simulation.
        mouse_norm_x/y: -1.0 to 1.0 (screen center is 0,0)
        """
        if self.warp_active:
             # --- Cinematic Warp Logic ---
             # Exponential acceleration
             self.warp_speed *= 1.12
             if self.warp_speed > 200: self.warp_speed = 200 # Cap speed

             # Move Z towards camera (decrease Z)
             # Points are roughly [-800, 800]. Camera is at ~-1200.
             self.points[:, 2] -= self.warp_speed

             # Respawn stars that pass behind the camera
             # Z < -1500 (allow some buffer)
             mask_behind = self.points[:, 2] < -1500

             respawn_count = np.sum(mask_behind)
             if respawn_count > 0:
                 # Respawn far ahead
                 self.points[mask_behind, 2] = 1600
                 # Randomize X/Y for infinite tunnel effect
                 self.points[mask_behind, 0] = (self.rng.random(respawn_count) - 0.5) * 2000
                 self.points[mask_behind, 1] = (self.rng.random(respawn_count) - 0.5) * 2000

             # Also slightly drift rotation to center
             self.target_rot_x = 0
             self.target_rot_y = 0
             self.rot_x *= 0.9
             self.rot_y *= 0.9

        else:
            # --- Standard Idle Logic ---
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
            mask_high = self.points > limit
            mask_low = self.points < -limit
            self.velocities[mask_high] *= -1
            self.velocities[mask_low] *= -1
            self.points[mask_high] = limit
            self.points[mask_low] = -limit

        # 3. Update Breathing Phases
        self.phases += self.phase_speeds

        # 4. Update Pulses
        # Filter out finished pulses
        active_pulses = []
        for p in self.pulses:
            p[2] += p[3] # Progress += Speed
            if p[2] < 1.0:
                active_pulses.append(p)
        self.pulses = active_pulses

        # Randomly spawn new pulses (Only if not warping, to reduce noise?)
        # Or keep them for effect? Let's keep them but maybe less chance if warping
        chance = 0.05 if self.warp_active else 0.15

        if self.connections and random.random() < chance:
            conn = random.choice(self.connections)
            speed = random.uniform(0.05, 0.1) if self.warp_active else random.uniform(0.02, 0.05)
            self.pulses.append([conn[0], conn[1], 0.0, speed])

    def _rotate_points(self):
        """Calculates the rotated 3D coordinates."""
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

        return x_final, y_final, z_final

    def _project_points(self, x_final, y_final, z_final, center_x, center_y, focal_length):
        """Projects 3D points to 2D coordinates."""
        # Avoid division by zero
        z_safe = z_final + 1200 # Push everything back so camera isn't inside
        scale = focal_length / np.maximum(z_safe, 0.1)

        x_2d = x_final * scale + center_x
        y_2d = y_final * scale + center_y

        return x_2d, y_2d, z_safe, scale

    def _draw_connections(self, painter, x_final, y_final, z_final, x_2d, y_2d, z_safe):
        """Draws connection lines between close nodes."""
        self.connections = []
        painter.setPen(QColor(100, 200, 255, 40)) # Very faint blue

        # Calculate distances
        pos_3d = np.column_stack((x_final, y_final, z_final))
        diff = pos_3d[:, np.newaxis, :] - pos_3d[np.newaxis, :, :]
        dists_sq = np.sum(diff**2, axis=-1)

        # Get pairs (i < j) where dist < limit
        mask = np.triu(dists_sq < self.connect_distance_sq, k=1)
        rows, cols = np.nonzero(mask)

        # Draw Lines
        for i, j in zip(rows, cols):
            # Optimization: Skip if either point is behind camera or too close
            if z_safe[i] < 10 or z_safe[j] < 10: continue

            p1 = QPointF(x_2d[i], y_2d[i])
            p2 = QPointF(x_2d[j], y_2d[j])

            # Opacity based on distance (closer = opaque)
            d_sq = dists_sq[i, j]
            alpha = int(255 * (1.0 - (d_sq / self.connect_distance_sq)))
            if alpha > 0:
                self.connections.append((i, j, d_sq))

                color = QColor(147, 197, 253) # Blue 300
                color.setAlpha(max(0, min(80, int(alpha * 0.3)))) # Cap alpha
                painter.setPen(color)
                painter.drawLine(p1, p2)

    def _draw_pulses(self, painter, x_2d, y_2d):
        """Draws moving pulses along connections."""
        painter.setPen(Qt.PenStyle.NoPen) # No outline

        for p in self.pulses:
            start_idx, end_idx, progress, _ = p

            # Check safety
            if start_idx >= len(x_2d) or end_idx >= len(x_2d): continue

            sx, sy = x_2d[start_idx], y_2d[start_idx]
            ex, ey = x_2d[end_idx], y_2d[end_idx]

            curr_x = sx + (ex - sx) * progress
            curr_y = sy + (ey - sy) * progress

            # Draw glowing dot
            offset = 8 # size 16 / 2

            painter.setOpacity(0.8)
            painter.drawPixmap(int(curr_x - offset), int(curr_y - offset), self.star_textures[16])
            painter.setOpacity(1.0)

    def _draw_nodes(self, painter, x_2d, y_2d, z_safe, scale):
        """Draws the star nodes sorted by Z-depth."""
        sort_indices = np.argsort(z_safe)[::-1] # Descending order of depth (Back to Front)

        for i in sort_indices:
            if z_safe[i] < 1: continue # Clip behind camera

            # Calculate size based on depth + breathing
            base_size = scale[i] * 10 # Base radius factor
            breath = 1.0 + math.sin(self.phases[i]) * 0.2
            final_size = base_size * breath

            # Cap max size to avoid giant blobs when hitting camera
            final_size = min(final_size, 100)

            # Choose texture bucket
            if final_size < 12: tex_key = 16
            elif final_size < 24: tex_key = 32
            else: tex_key = 64

            tex = self.star_textures[tex_key]

            x = x_2d[i] - (tex.width() / 2)
            y = y_2d[i] - (tex.height() / 2)

            # Depth opacity
            depth_alpha = min(1.0, max(0.2, (scale[i] * 2.0)))
            painter.setOpacity(depth_alpha)

            painter.drawPixmap(int(x), int(y), tex)

        painter.setOpacity(1.0)

    def project_and_render(self, painter, width, height):
        """
        Projects 3D points to 2D and renders everything.
        Doing projection + render in one pass to avoid copying large arrays back to Python.
        """
        center_x = width / 2
        center_y = height / 2
        focal_length = 800

        # --- 1. Rotation Matrices ---
        x_final, y_final, z_final = self._rotate_points()

        # --- 2. Perspective Projection ---
        x_2d, y_2d, z_safe, scale = self._project_points(x_final, y_final, z_final, center_x, center_y, focal_length)

        # --- 3. Draw Connections ---
        self._draw_connections(painter, x_final, y_final, z_final, x_2d, y_2d, z_safe)

        # --- 4. Draw Pulses ---
        self._draw_pulses(painter, x_2d, y_2d)

        # --- 5. Draw Nodes (Z-Sorted) ---
        self._draw_nodes(painter, x_2d, y_2d, z_safe, scale)
