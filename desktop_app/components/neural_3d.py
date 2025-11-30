import math
import random
import numpy as np
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QRadialGradient, QPixmap, QPainter, QBrush, QImage

class NeuralNetwork3D:
    def __init__(self, num_nodes=100, connect_distance=250):
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

    def update(self, mouse_norm_x, mouse_norm_y):
        """
        Updates the simulation.
        mouse_norm_x/y: -1.0 to 1.0 (screen center is 0,0)
        """
        # 1. Update Rotation Target (Smooth Camera)
        # Mouse movement implies looking around or rotating the object
        self.target_rot_y = mouse_norm_x * 0.5 # Yaw
        self.target_rot_x = -mouse_norm_y * 0.5 # Pitch

        # Lerp rotation
        lerp_speed = 0.05
        self.rot_x += (self.target_rot_x - self.rot_x) * lerp_speed
        self.rot_y += (self.target_rot_y - self.rot_y) * lerp_speed

        # 2. Update Positions (Drift)
        self.points += self.velocities

        # Wrap around boundary (Torus topology-ish or just box bounce)
        # Using box bounce for simplicity, or wrap
        limit = 1000
        # Numpy boolean indexing for boundary check
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

        # Randomly spawn new pulses
        if self.connections and random.random() < 0.15: # 15% chance per frame
            conn = random.choice(self.connections)
            # [start_idx, end_idx, progress, speed]
            speed = random.uniform(0.02, 0.05)
            self.pulses.append([conn[0], conn[1], 0.0, speed])


    def project_and_render(self, painter, width, height):
        """
        Projects 3D points to 2D and renders everything.
        Doing projection + render in one pass to avoid copying large arrays back to Python.
        """
        center_x = width / 2
        center_y = height / 2
        focal_length = 800

        # --- 1. Rotation Matrices ---
        cx, sx = math.cos(self.rot_x), math.sin(self.rot_x)
        cy, sy = math.cos(self.rot_y), math.sin(self.rot_y)

        # Rotate around Y axis
        # x' = x*cos - z*sin
        # z' = x*sin + z*cos
        x = self.points[:, 0]
        y = self.points[:, 1]
        z = self.points[:, 2]

        x_rot_y = x * cy - z * sy
        z_rot_y = x * sy + z * cy

        # Rotate around X axis
        # y' = y*cos - z'*sin
        # z'' = y*sin + z'*cos
        y_final = y * cx - z_rot_y * sx
        z_final = y * sx + z_rot_y * cx
        x_final = x_rot_y

        # --- 2. Perspective Projection ---
        # scale = f / (f + z)
        # Avoid division by zero
        z_safe = z_final + 1200 # Push everything back so camera isn't inside
        scale = focal_length / np.maximum(z_safe, 0.1)

        x_2d = x_final * scale + center_x
        y_2d = y_final * scale + center_y

        # Store 2D coords for connection drawing
        # Shape (N, 2)
        coords_2d = np.column_stack((x_2d, y_2d))

        # --- 3. Draw Connections & Pulses ---
        # Calculating distances in 3D is better for logic, but 2D is faster for culling visuals.
        # Let's use Z-sorted rendering for nodes, but connections first (behind nodes).

        # Re-calculate connections periodically or every frame?
        # For N=100, N^2 = 10000 checks. Numpy is fast enough for every frame.

        # Calculate squared distance matrix (N x N)
        # Using broadcasting: (N, 1, 3) - (1, N, 3) -> (N, N, 3)
        # This might be memory heavy if N is huge. For N=100 it's tiny.
        # Let's stick to a simpler loop for connections or scipy cdist if available.
        # Since we want "Unthinkable" performance, let's optimize the loop logic.

        # Actually, for visual connections, we only care about screen space or 3D space proximity.
        # Let's use 3D proximity.

        self.connections = []
        painter.setPen(QColor(100, 200, 255, 40)) # Very faint blue

        # Optimization: Only check a subset or use a spatial structure?
        # For N=100, brute force is fine in C (numpy), but traversing in Python is slow.
        # We'll rely on numpy for the distance calculation.

        # pos_3d = np.column_stack((x_final, y_final, z_final))
        # dists = np.sum((pos_3d[:, np.newaxis, :] - pos_3d[np.newaxis, :, :]) ** 2, axis=-1)
        # This is (100, 100).

        # Using pure numpy to find indices where dist < threshold
        # triu to avoid duplicates and self-connection
        # indices = np.argwhere(np.triu(dists < self.connect_distance_sq, k=1))

        # Calculating matrix every frame for N=150 might be slightly heavy for Python overhead?
        # Let's try.
        pos_3d = np.column_stack((x_final, y_final, z_final))
        diff = pos_3d[:, np.newaxis, :] - pos_3d[np.newaxis, :, :]
        dists_sq = np.sum(diff**2, axis=-1)

        # Get pairs (i < j) where dist < limit
        mask = np.triu(dists_sq < self.connect_distance_sq, k=1)
        rows, cols = np.nonzero(mask)

        # Draw Lines
        lines = []
        for i, j in zip(rows, cols):
            p1 = QPointF(x_2d[i], y_2d[i])
            p2 = QPointF(x_2d[j], y_2d[j])

            # Opacity based on distance (closer = opaque)
            d_sq = dists_sq[i, j]
            alpha = int(255 * (1.0 - (d_sq / self.connect_distance_sq)))
            if alpha > 0:
                # Store connection for pulses
                self.connections.append((i, j, d_sq))

                # Draw Line
                color = QColor(147, 197, 253) # Blue 300
                color.setAlpha(max(0, min(80, int(alpha * 0.3)))) # Cap alpha
                painter.setPen(color)
                painter.drawLine(p1, p2)

        # Draw Pulses
        painter.setPen(Qt.PenStyle.NoPen) # No outline
        pulse_color = QColor(255, 255, 255) # White core

        for p in self.pulses:
            start_idx, end_idx, progress, _ = p

            # Interpolate 2D position
            sx, sy = x_2d[start_idx], y_2d[start_idx]
            ex, ey = x_2d[end_idx], y_2d[end_idx]

            curr_x = sx + (ex - sx) * progress
            curr_y = sy + (ey - sy) * progress

            # Draw glowing dot
            # Using one of the small textures
            size = 16
            offset = size / 2

            # Simple distance fading for pulses too?
            pulse_color.setAlpha(200)
            painter.setOpacity(0.8)
            painter.drawPixmap(int(curr_x - offset), int(curr_y - offset), self.star_textures[16])
            painter.setOpacity(1.0)


        # --- 4. Draw Nodes (Z-Sorted) ---
        # Sort by Z (depth) so we draw far ones first
        # z_final is high = close? No.
        # In this coord system:
        # z_safe = z_final + 1200. Higher z_safe = further away?
        # No, scale = f / z_safe. So larger z_safe means smaller scale -> further away.
        # We want to draw largest z_safe (furthest) first.

        sort_indices = np.argsort(z_safe)[::-1] # Descending order of depth (Back to Front)

        for i in sort_indices:
            # Calculate size based on depth + breathing
            base_size = scale[i] * 10 # Base radius factor
            breath = 1.0 + math.sin(self.phases[i]) * 0.2
            final_size = base_size * breath

            # Choose texture bucket
            # 8, 16, 32, 64
            if final_size < 12: tex_key = 16
            elif final_size < 24: tex_key = 32
            else: tex_key = 64

            tex = self.star_textures[tex_key]

            # Scale pixmap if needed or just use raw?
            # Scaling pixmaps every frame is slow.
            # Better to just use the bucket size and rely on alpha for distance cue?
            # Or just draw it centered.

            # Let's scale slightly using the painter transform if needed,
            # but drawing fixed sprites is faster.
            # Let's map strict size buckets to avoid scaling artifacts/cost.

            x = x_2d[i] - (tex.width() / 2)
            y = y_2d[i] - (tex.height() / 2)

            # Depth opacity
            # Normalized depth 0..1
            depth_alpha = min(1.0, max(0.2, (scale[i] * 2.0)))
            painter.setOpacity(depth_alpha)

            painter.drawPixmap(int(x), int(y), tex)

        painter.setOpacity(1.0)
