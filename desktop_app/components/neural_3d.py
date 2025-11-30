import math
import random
import numpy as np
from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import QColor, QRadialGradient, QPixmap, QPainter, QBrush, QImage, QPen

class NeuralNetwork3D:
    def __init__(self, num_nodes=160, connect_distance=300):
        self.num_nodes = num_nodes
        self.connect_distance_sq = connect_distance ** 2

        # --- 3D State (Vectorized) ---
        # Position X, Y, Z centered at 0,0,0
        # Increased range for more depth
        self.points = (np.random.rand(num_nodes, 3) - 0.5) * 2000

        # Velocity vector (slow drift)
        self.velocities = (np.random.rand(num_nodes, 3) - 0.5) * 0.8

        # Phase for "breathing" effect (0 to 2pi)
        self.phases = np.random.rand(num_nodes) * 2 * math.pi
        self.phase_speeds = np.random.rand(num_nodes) * 0.03 + 0.01

        # Current Rotation (Euler angles)
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.target_rot_x = 0.0
        self.target_rot_y = 0.0

        # Camera Drift (Z-axis movement)
        self.camera_z = 0.0
        self.camera_speed = 1.2

        # --- Pulse System ---
        # List of active pulses: [start_index, end_index, progress (0.0-1.0), speed]
        self.pulses = []
        self.connections = [] # Cached connections [(i, j, dist_sq)]

        # --- Pre-calculated Assets ---
        self.star_textures = self._generate_star_textures()

    def _generate_star_textures(self):
        """Pre-renders glowing star textures at different sizes."""
        textures = {}
        # Sizes for different depths/importance
        sizes = [8, 16, 32, 64, 128]
        # Cyber Blue / White core
        base_color = QColor(60, 160, 255)

        for size in sizes:
            img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
            img.fill(0)

            painter = QPainter(img)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Complex Gradient for realistic glow
            grad = QRadialGradient(size/2, size/2, size/2)

            c_core = QColor(255, 255, 255, 255) # White Hot Core
            c_mid = QColor(100, 200, 255, 180)  # Bright Blue Mid
            c_edge = QColor(0, 50, 150, 0)      # Fade to transparent

            grad.setColorAt(0.0, c_core)
            grad.setColorAt(0.15, c_core)
            grad.setColorAt(0.4, c_mid)
            grad.setColorAt(1.0, c_edge)

            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()

            textures[size] = QPixmap.fromImage(img)

        return textures

    def update(self, mouse_norm_x, mouse_norm_y):
        """
        Updates the simulation.
        mouse_norm_x/y: -1.0 to 1.0
        """
        # 1. Update Rotation Target (Smooth Camera)
        self.target_rot_y = mouse_norm_x * 0.8 # Yaw
        self.target_rot_x = -mouse_norm_y * 0.6 # Pitch

        # Lerp rotation
        lerp_speed = 0.04
        self.rot_x += (self.target_rot_x - self.rot_x) * lerp_speed
        self.rot_y += (self.target_rot_y - self.rot_y) * lerp_speed

        # 2. Update Positions (Drift + Camera Z)
        self.points += self.velocities

        # Simulate forward camera movement by moving points backwards relative to camera
        # actually, let's just shift Z and wrap
        self.points[:, 2] -= self.camera_speed

        # Wrap around boundary
        limit = 1200
        # Z-wrap is special for infinite fly-through feel
        mask_z_low = self.points[:, 2] < -limit
        self.points[mask_z_low, 2] += 2 * limit

        # Standard bounce/wrap for X/Y
        mask_high = self.points > limit
        mask_low = self.points < -limit

        # Reflect velocities on X/Y walls for containment
        self.velocities[mask_high[:, 0:2], 0:2] *= -1
        self.velocities[mask_low[:, 0:2], 0:2] *= -1

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

        # Spawn new pulses randomly
        if self.connections and random.random() < 0.25: # Higher activity
            conn = random.choice(self.connections)
            speed = random.uniform(0.015, 0.04)
            self.pulses.append([conn[0], conn[1], 0.0, speed])


    def project_and_render(self, painter, width, height):
        center_x = width / 2
        center_y = height / 2
        focal_length = 900 # Wider FOV

        # --- 1. Rotation Matrices ---
        cx, sx = math.cos(self.rot_x), math.sin(self.rot_x)
        cy, sy = math.cos(self.rot_y), math.sin(self.rot_y)

        # Vectorized Rotation
        x = self.points[:, 0]
        y = self.points[:, 1]
        z = self.points[:, 2]

        # Rotate around Y
        x_rot_y = x * cy - z * sy
        z_rot_y = x * sy + z * cy

        # Rotate around X
        y_final = y * cx - z_rot_y * sx
        z_final = y * sx + z_rot_y * cx
        x_final = x_rot_y

        # --- 2. Perspective Projection ---
        # Push camera back to view the scene
        z_camera_offset = 1400
        z_safe = z_final + z_camera_offset

        # Clip points behind camera
        mask_visible = z_safe > 100

        # Apply mask to everything we'll use
        # (This avoids projecting points behind the camera which causes glitches)
        # Note: If we just ignore them, connections might look weird if one end is clipped.
        # For simplicity in this visualizer, we just hide nodes behind camera.

        # To keep indices aligned for connections, we calculate everything but only draw valid ones.
        # But scale calculation needs protection.
        scale = np.zeros_like(z_safe)
        scale[mask_visible] = focal_length / z_safe[mask_visible]

        x_2d = x_final * scale + center_x
        y_2d = y_final * scale + center_y

        # --- 3. Connections Logic ---
        # Calculate squared distances in 3D (more accurate)
        pos_3d = np.column_stack((x_final, y_final, z_final))

        # Optimization: Only calculate distances for a subset or use cdist?
        # Pure numpy broadcasting for 160 points is (160, 160, 3) which is ~76KB floats. Fast.
        diff = pos_3d[:, np.newaxis, :] - pos_3d[np.newaxis, :, :]
        dists_sq = np.sum(diff**2, axis=-1)

        # Filter connections
        # mask_conn: (i < j) & (dist < threshold)
        # Also ensure both points are visible (z_safe > 100)
        visible_flag = mask_visible.astype(int)
        # Outer product to check if both i and j are visible
        pair_visible = visible_flag[:, np.newaxis] * visible_flag[np.newaxis, :]

        mask = np.triu((dists_sq < self.connect_distance_sq) & (pair_visible == 1), k=1)
        rows, cols = np.nonzero(mask)

        self.connections = []

        # Setup Pen for Lines
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Lines
        # We can batch draw, but opacity varies by distance.
        for i, j in zip(rows, cols):
            d_sq = dists_sq[i, j]

            # Depth Fade (Fog)
            # Average Z of the two points
            avg_z = (z_safe[i] + z_safe[j]) / 2.0

            # Opacity based on connection length AND depth
            # Closer points (low d_sq) = stronger
            # Closer to camera (low avg_z) = stronger

            conn_strength = 1.0 - (d_sq / self.connect_distance_sq)
            depth_strength = max(0.0, min(1.0, 1.0 - (avg_z - 600) / 2000)) # Fade out after z=600

            alpha = int(255 * conn_strength * depth_strength * 0.4) # Max 40% opacity for lines

            if alpha > 5:
                # Store valid connection for pulses
                self.connections.append((i, j, d_sq))

                p1 = QPointF(x_2d[i], y_2d[i])
                p2 = QPointF(x_2d[j], y_2d[j])

                color = QColor(100, 200, 255)
                color.setAlpha(alpha)
                painter.setPen(color)
                painter.drawLine(p1, p2)

        # Draw Pulses
        # Use additive blending simulation by drawing bright sprites
        for p in self.pulses:
            start_idx, end_idx, progress, _ = p

            # Check visibility
            if not (mask_visible[start_idx] and mask_visible[end_idx]):
                continue

            sx, sy = x_2d[start_idx], y_2d[start_idx]
            ex, ey = x_2d[end_idx], y_2d[end_idx]

            curr_x = sx + (ex - sx) * progress
            curr_y = sy + (ey - sy) * progress

            # Pulse size scales with depth
            z_interp = z_safe[start_idx] + (z_safe[end_idx] - z_safe[start_idx]) * progress
            p_scale = focal_length / z_interp if z_interp > 1 else 0

            size = int(12 * p_scale)
            if size > 0:
                # Use cached texture 16 or 32
                tex_key = 16 if size < 20 else 32
                tex = self.star_textures[tex_key]

                # Draw
                painter.setOpacity(0.9)
                painter.drawPixmap(int(curr_x - tex.width()/2), int(curr_y - tex.height()/2), tex)

        # --- 4. Draw Nodes ---
        # Sort by depth (far to near)
        # We only draw visible nodes
        visible_indices = np.where(mask_visible)[0]
        # Sort these indices by z_safe descending
        sorted_indices = visible_indices[np.argsort(z_safe[visible_indices])[::-1]]

        for i in sorted_indices:
            s = scale[i]

            # Base size logic
            base_size = s * 15 # Base pixel radius

            # Breathing
            breath = 1.0 + math.sin(self.phases[i]) * 0.3
            final_size = base_size * breath

            # Depth Fade (Fog)
            depth_alpha = max(0.0, min(1.0, 1.0 - (z_safe[i] - 500) / 2500))

            if final_size < 1 or depth_alpha <= 0.05:
                continue

            # Select Texture
            if final_size < 12: tex_key = 8
            elif final_size < 24: tex_key = 16
            elif final_size < 48: tex_key = 32
            elif final_size < 96: tex_key = 64
            else: tex_key = 128

            tex = self.star_textures[tex_key]

            # Draw centered
            x = x_2d[i] - (tex.width() / 2)
            y = y_2d[i] - (tex.height() / 2)

            painter.setOpacity(depth_alpha)
            painter.drawPixmap(int(x), int(y), tex)

        painter.setOpacity(1.0)
