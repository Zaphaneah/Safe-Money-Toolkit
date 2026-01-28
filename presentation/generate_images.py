#!/usr/bin/env python3
"""
Generate beautiful, thematic artwork for the Bible class presentation.
Creates meaningful symbolic imagery using Pillow with jewel-tone palettes.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# Image dimensions (16:9 at high resolution)
W, H = 1920, 1080

# Jewel-tone color palette
DEEP_PURPLE = (48, 15, 72)
BURGUNDY = (128, 0, 32)
DARK_BURGUNDY = (80, 10, 25)
GOLD = (218, 165, 32)
LIGHT_GOLD = (255, 215, 100)
PALE_GOLD = (255, 235, 180)
DEEP_TEAL = (0, 80, 80)
DARK_TEAL = (0, 50, 55)
WARM_WHITE = (255, 248, 240)
CREAM = (255, 245, 230)
NEAR_BLACK = (15, 10, 20)
DARK_BG = (20, 12, 30)
RICH_PURPLE = (75, 25, 110)
SOFT_PURPLE = (100, 50, 140)
ROYAL_BLUE = (30, 30, 90)
MIDNIGHT = (10, 5, 25)


def lerp_color(c1, c2, t):
    """Linear interpolation between two colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def create_gradient(draw, width, height, color1, color2, direction="vertical"):
    """Create a smooth gradient."""
    for i in range(height if direction == "vertical" else width):
        t = i / (height if direction == "vertical" else width)
        color = lerp_color(color1, color2, t)
        if direction == "vertical":
            draw.line([(0, i), (width, i)], fill=color)
        else:
            draw.line([(i, 0), (i, height)], fill=color)


def create_radial_gradient(img, center, radius, color_inner, color_outer):
    """Create a radial gradient effect."""
    pixels = img.load()
    cx, cy = center
    for y in range(img.height):
        for x in range(img.width):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            t = min(dist / radius, 1.0)
            t = t * t  # Ease-in for smoother falloff
            color = lerp_color(color_inner, color_outer, t)
            # Blend with existing pixel
            existing = pixels[x, y][:3]
            blended = lerp_color(color, existing, 0.3)
            pixels[x, y] = blended


def add_light_rays(draw, cx, cy, num_rays=12, length=800, color=(255, 215, 100)):
    """Add subtle light rays emanating from a point."""
    for i in range(num_rays):
        angle = (2 * math.pi * i / num_rays) + random.uniform(-0.1, 0.1)
        x_end = cx + math.cos(angle) * length
        y_end = cy + math.sin(angle) * length
        for w in range(3, 0, -1):
            alpha_color = lerp_color(color, NEAR_BLACK, 0.5 + w * 0.15)
            draw.line([(cx, cy), (x_end, y_end)], fill=alpha_color, width=w)


def draw_cross(draw, cx, cy, size, thickness, color, glow=True):
    """Draw a cross with optional glow effect."""
    half = size // 2
    t = thickness // 2

    if glow:
        # Glow layers
        for g in range(6, 0, -1):
            glow_color = lerp_color(color, NEAR_BLACK, 0.3 + g * 0.1)
            gt = t + g * 4
            # Vertical beam
            draw.rectangle([cx - gt, cy - half - g * 3, cx + gt, cy + half + g * 3], fill=glow_color)
            # Horizontal beam (crossbar at ~1/3 from top)
            crossbar_y = cy - half // 3
            draw.rectangle([cx - half // 2 - g * 3, crossbar_y - gt, cx + half // 2 + g * 3, crossbar_y + gt], fill=glow_color)

    # Main cross
    # Vertical beam
    draw.rectangle([cx - t, cy - half, cx + t, cy + half], fill=color)
    # Horizontal beam
    crossbar_y = cy - half // 3
    draw.rectangle([cx - half // 2, crossbar_y - t, cx + half // 2, crossbar_y + t], fill=color)


def add_stars(draw, count=50, region=(0, 0, W, H)):
    """Add subtle star points."""
    for _ in range(count):
        x = random.randint(region[0], region[2])
        y = random.randint(region[1], region[3])
        brightness = random.randint(150, 255)
        size = random.choice([1, 1, 1, 2])
        color = (brightness, brightness, brightness - random.randint(0, 30))
        if size == 1:
            draw.point((x, y), fill=color)
        else:
            draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=color)


def add_bokeh(img, count=15, min_r=20, max_r=80):
    """Add soft bokeh circles for depth."""
    overlay = Image.new("RGB", img.size, (0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    for _ in range(count):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r = random.randint(min_r, max_r)
        alpha = random.randint(15, 40)
        color = lerp_color(GOLD, WARM_WHITE, random.random())
        color_dim = lerp_color(color, (0, 0, 0), 1 - alpha / 255)
        draw_overlay.ellipse([x - r, y - r, x + r, y + r], fill=color_dim)
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=15))
    # Screen blend
    from PIL import ImageChops
    img_result = ImageChops.add(img, overlay)
    return img_result


def draw_descending_steps(draw, x_start, y_start, num_steps, step_w, step_h, color1, color2):
    """Draw descending staircase pattern."""
    for i in range(num_steps):
        t = i / (num_steps - 1)
        color = lerp_color(color1, color2, t)
        x = x_start + i * step_w
        y = y_start + i * step_h
        # Step surface
        draw.rectangle([x, y, x + step_w, y + step_h * 4], fill=color)
        # Step edge highlight
        highlight = lerp_color(color, WARM_WHITE, 0.3)
        draw.rectangle([x, y, x + step_w, y + 3], fill=highlight)


# ============================================================
# SLIDE 2: Cross / Mindset of Christ
# ============================================================
def generate_slide2_cross_mindset():
    """Dramatic cross against deep purple-gold sky with light rays."""
    img = Image.new("RGB", (W, H), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Gradient sky: deep purple to dark burgundy
    create_gradient(draw, W, H, DEEP_PURPLE, DARK_BURGUNDY)

    # Add stars in upper portion
    add_stars(draw, count=80, region=(0, 0, W, H // 2))

    # Golden light source behind cross
    add_light_rays(draw, W // 2, H // 3, num_rays=24, length=900, color=GOLD)

    # Central radial glow
    create_radial_gradient(img, (W // 2, H // 3), 500, LIGHT_GOLD, DEEP_PURPLE)
    draw = ImageDraw.Draw(img)

    # Draw the main cross
    draw_cross(draw, W // 2, H // 2 - 30, 500, 40, WARM_WHITE, glow=True)

    # Add soft bokeh
    img = add_bokeh(img, count=10, min_r=30, max_r=60)

    # Slight vignette
    vignette = Image.new("RGB", (W, H), (0, 0, 0))
    vignette_draw = ImageDraw.Draw(vignette)
    create_radial_gradient(vignette, (W // 2, H // 2), 1200, (60, 60, 60), (0, 0, 0))
    from PIL import ImageChops
    img = ImageChops.add(img, vignette)

    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    img.save(os.path.join(IMAGE_DIR, "slide2_cross_mindset.jpg"), "JPEG", quality=95)
    print("  Generated: slide2_cross_mindset.jpg")


# ============================================================
# SLIDE 3: Incarnation - God With Us
# ============================================================
def generate_slide3_incarnation():
    """Bethlehem star / divine light descending to earth."""
    img = Image.new("RGB", (W, H), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Night sky gradient
    create_gradient(draw, W, H, MIDNIGHT, DEEP_TEAL)

    # Starfield
    add_stars(draw, count=200, region=(0, 0, W, H * 2 // 3))

    # Bright Bethlehem star at top
    star_x, star_y = W // 2, 120
    # Star glow
    for r in range(120, 0, -2):
        t = r / 120
        color = lerp_color(WARM_WHITE, DEEP_PURPLE, t)
        draw.ellipse([star_x - r, star_y - r, star_x + r, star_y + r], fill=color)

    # Star points (4-pointed)
    for angle_offset in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
        for length in [200, 150]:
            x_end = star_x + math.cos(angle_offset) * length
            y_end = star_y + math.sin(angle_offset) * length
            draw.line([(star_x, star_y), (x_end, y_end)], fill=WARM_WHITE, width=2)
            draw.line([(star_x, star_y), (x_end, y_end)], fill=LIGHT_GOLD, width=1)

    # Diagonal star points
    for angle_offset in [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]:
        x_end = star_x + math.cos(angle_offset) * 100
        y_end = star_y + math.sin(angle_offset) * 100
        draw.line([(star_x, star_y), (x_end, y_end)], fill=PALE_GOLD, width=1)

    # Light beam descending from star to earth
    beam_width_top = 20
    beam_width_bottom = 300
    for y in range(star_y + 60, H):
        t = (y - star_y - 60) / (H - star_y - 60)
        bw = beam_width_top + (beam_width_bottom - beam_width_top) * t
        alpha = int(40 * (1 - t * 0.7))
        color = lerp_color(LIGHT_GOLD, DEEP_TEAL, t * 0.8)
        color_bright = lerp_color(color, WARM_WHITE, 0.2)
        left = int(star_x - bw / 2)
        right = int(star_x + bw / 2)
        # Soft beam
        for x in range(max(0, left), min(W, right)):
            dx = abs(x - star_x) / (bw / 2)
            brightness = max(0, 1 - dx * dx)
            px = img.getpixel((x, y))
            new_color = lerp_color(px[:3], color_bright, brightness * 0.3)
            img.putpixel((x, y), new_color)

    draw = ImageDraw.Draw(img)

    # Earth/ground at bottom
    for y in range(H - 150, H):
        t = (y - (H - 150)) / 150
        color = lerp_color(DARK_TEAL, NEAR_BLACK, t)
        draw.line([(0, y), (W, y)], fill=color)

    # Silhouette of simple manger/stable
    manger_cx = W // 2
    manger_base = H - 80
    # Simple A-frame
    points = [
        (manger_cx - 120, manger_base),
        (manger_cx, manger_base - 100),
        (manger_cx + 120, manger_base),
    ]
    draw.polygon(points, fill=(10, 5, 15))
    # Doorway
    draw.rectangle([manger_cx - 30, manger_base - 60, manger_cx + 30, manger_base], fill=(10, 5, 15))
    # Tiny golden glow in doorway
    for r in range(20, 0, -1):
        t = r / 20
        color = lerp_color(LIGHT_GOLD, (10, 5, 15), t)
        draw.ellipse([manger_cx - r, manger_base - 40 - r // 2, manger_cx + r, manger_base - 40 + r // 2], fill=color)

    img = add_bokeh(img, count=8, min_r=15, max_r=40)
    img.save(os.path.join(IMAGE_DIR, "slide3_incarnation.jpg"), "JPEG", quality=95)
    print("  Generated: slide3_incarnation.jpg")


# ============================================================
# SLIDE 4: He Emptied Himself - Kenosis
# ============================================================
def generate_slide4_emptying():
    """Vessel pouring out golden light - symbolic of kenosis."""
    img = Image.new("RGB", (W, H), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Dark purple gradient background
    create_gradient(draw, W, H, RICH_PURPLE, NEAR_BLACK)

    # Chalice/vessel shape (upper right area)
    vessel_cx, vessel_cy = W * 2 // 3, H // 3

    # Vessel body (tilted as if pouring)
    # Simple elegant chalice shape using ellipses and lines
    # Bowl
    draw.ellipse([vessel_cx - 80, vessel_cy - 50, vessel_cx + 80, vessel_cy + 10], outline=GOLD, width=3)
    draw.arc([vessel_cx - 80, vessel_cy - 50, vessel_cx + 80, vessel_cy + 10], 0, 180, fill=GOLD, width=3)
    # Stem
    draw.line([(vessel_cx, vessel_cy + 10), (vessel_cx, vessel_cy + 80)], fill=GOLD, width=3)
    # Base
    draw.ellipse([vessel_cx - 40, vessel_cy + 70, vessel_cx + 40, vessel_cy + 90], outline=GOLD, width=2)

    # Pouring light stream from vessel (cascading down-left)
    pour_start_x = vessel_cx - 60
    pour_start_y = vessel_cy - 20
    num_particles = 500
    random.seed(42)
    for _ in range(num_particles):
        t = random.random()
        spread = t * 200
        x = pour_start_x - t * 400 + random.gauss(0, spread * 0.3)
        y = pour_start_y + t * 600 + random.gauss(0, 20)
        brightness = 1 - t * 0.6
        size = max(1, int(3 * brightness))
        color = lerp_color(LIGHT_GOLD, DEEP_PURPLE, t * 0.7)
        color_bright = lerp_color(color, WARM_WHITE, brightness * 0.5)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color_bright)

    # Larger golden drops
    for i in range(30):
        t = i / 30
        x = pour_start_x - t * 350 + random.gauss(0, t * 60)
        y = pour_start_y + t * 550 + random.gauss(0, 15)
        r = random.randint(3, 8)
        color = lerp_color(WARM_WHITE, GOLD, t)
        # Glow
        for gr in range(r + 6, r, -1):
            gc = lerp_color(color, DEEP_PURPLE, (gr - r) / 6)
            draw.ellipse([x - gr, y - gr, x + gr, y + gr], fill=gc)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    # Add subtle background particles
    add_stars(draw, count=60, region=(0, 0, W, H))

    img = add_bokeh(img, count=12, min_r=20, max_r=50)
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    img.save(os.path.join(IMAGE_DIR, "slide4_emptying.jpg"), "JPEG", quality=95)
    print("  Generated: slide4_emptying.jpg")


# ============================================================
# SLIDE 5: He Humbled Himself - Feet washing
# ============================================================
def generate_slide5_humble():
    """Hands in humble posture with water and light - feet washing symbolism."""
    img = Image.new("RGB", (W, H), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Warm dark gradient
    create_gradient(draw, W, H, DARK_BURGUNDY, NEAR_BLACK)

    # Gentle warm light from above
    create_radial_gradient(img, (W // 2, 0), 900, (80, 40, 20), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Basin/bowl shape at center-bottom
    basin_cx, basin_cy = W // 2, H * 2 // 3
    # Outer bowl
    draw.ellipse([basin_cx - 200, basin_cy - 40, basin_cx + 200, basin_cy + 60], outline=GOLD, width=3)
    draw.arc([basin_cx - 200, basin_cy - 40, basin_cx + 200, basin_cy + 60], 0, 180, fill=GOLD, width=3)
    # Water surface reflection
    for y_off in range(0, 50, 2):
        t = y_off / 50
        color = lerp_color((40, 60, 80), NEAR_BLACK, t)
        x_shrink = int(t * 60)
        draw.line([(basin_cx - 190 + x_shrink, basin_cy + y_off),
                    (basin_cx + 190 - x_shrink, basin_cy + y_off)], fill=color)

    # Water drops falling into basin
    for i in range(15):
        drop_y = basin_cy - 200 + i * 15
        drop_x = W // 2 + random.randint(-20, 20)
        size = max(1, 4 - i // 4)
        color = lerp_color(WARM_WHITE, (60, 80, 120), i / 15)
        draw.ellipse([drop_x - size, drop_y - size * 2, drop_x + size, drop_y + size], fill=color)

    # Ripples in water
    for r in range(20, 180, 25):
        opacity = max(0, 255 - r * 2)
        color = lerp_color((80, 100, 130), NEAR_BLACK, r / 180)
        draw.arc([basin_cx - r, basin_cy - r // 4, basin_cx + r, basin_cy + r // 4],
                 0, 180, fill=color, width=1)

    # Towel draped near basin (simple fabric suggestion)
    towel_pts = [
        (basin_cx + 180, basin_cy - 20),
        (basin_cx + 280, basin_cy - 60),
        (basin_cx + 300, basin_cy + 40),
        (basin_cx + 220, basin_cy + 80),
        (basin_cx + 190, basin_cy + 30),
    ]
    draw.polygon(towel_pts, fill=(180, 170, 150))
    # Fold lines
    draw.line([towel_pts[0], (basin_cx + 250, basin_cy)], fill=(150, 140, 120), width=1)
    draw.line([(basin_cx + 240, basin_cy - 30), (basin_cx + 260, basin_cy + 50)], fill=(150, 140, 120), width=1)

    # Soft candlelight effect in upper area
    for r in range(200, 0, -3):
        t = r / 200
        color = lerp_color(LIGHT_GOLD, DARK_BURGUNDY, t)
        draw.ellipse([W // 2 - r - 100, 50 - r // 3, W // 2 + r - 100, 50 + r // 3], fill=color)

    # Subtle cross shadow on wall
    cx_shadow, cy_shadow = W // 4, H // 4
    shadow_color = lerp_color(DARK_BURGUNDY, NEAR_BLACK, 0.5)
    draw.rectangle([cx_shadow - 3, cy_shadow - 80, cx_shadow + 3, cy_shadow + 80], fill=shadow_color)
    draw.rectangle([cx_shadow - 50, cy_shadow - 25 - 3, cx_shadow + 50, cy_shadow - 25 + 3], fill=shadow_color)

    img = add_bokeh(img, count=8, min_r=10, max_r=30)
    img.save(os.path.join(IMAGE_DIR, "slide5_humble.jpg"), "JPEG", quality=95)
    print("  Generated: slide5_humble.jpg")


# ============================================================
# SLIDE 6: Obedient to Death - The Cross
# ============================================================
def generate_slide6_cross_death():
    """Powerful, dramatic cross with thorns and dark sky."""
    img = Image.new("RGB", (W, H), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Dramatic dark sky with blood red at horizon
    for y in range(H):
        t = y / H
        if t < 0.4:
            color = lerp_color(NEAR_BLACK, DEEP_PURPLE, t / 0.4)
        elif t < 0.7:
            color = lerp_color(DEEP_PURPLE, BURGUNDY, (t - 0.4) / 0.3)
        else:
            color = lerp_color(BURGUNDY, NEAR_BLACK, (t - 0.7) / 0.3)
        draw.line([(0, y), (W, y)], fill=color)

    # Stars
    add_stars(draw, count=40, region=(0, 0, W, H // 3))

    # Three crosses (Golgotha)
    # Center cross (larger)
    draw_cross(draw, W // 2, H // 2 - 50, 550, 45, WARM_WHITE, glow=True)

    # Left cross (smaller, angled)
    draw_cross(draw, W // 4, H // 2 + 20, 380, 30, (180, 170, 160), glow=False)

    # Right cross (smaller, angled)
    draw_cross(draw, 3 * W // 4, H // 2 + 20, 380, 30, (180, 170, 160), glow=False)

    # Crown of thorns suggestion around center crossbar
    crown_cx = W // 2
    crown_cy = H // 2 - 50 - 550 // 3  # At crossbar
    for i in range(60):
        angle = 2 * math.pi * i / 60
        r = 50 + random.randint(-5, 5)
        x1 = crown_cx + math.cos(angle) * r
        y1 = crown_cy + math.sin(angle) * (r * 0.4)
        # Thorn point
        thorn_angle = angle + random.uniform(-0.3, 0.3)
        thorn_len = random.randint(8, 20)
        x2 = x1 + math.cos(thorn_angle) * thorn_len
        y2 = y1 + math.sin(thorn_angle) * thorn_len
        draw.line([(x1, y1), (x2, y2)], fill=(100, 70, 40), width=1)

    # Crown ring
    draw.ellipse([crown_cx - 50, crown_cy - 20, crown_cx + 50, crown_cy + 20],
                 outline=(100, 70, 40), width=2)

    # Ground/hill silhouette
    hill_points = [(0, H)]
    for x in range(0, W + 20, 20):
        y = H - 80 + 30 * math.sin(x / 200) + 15 * math.sin(x / 80)
        hill_points.append((x, y))
    hill_points.append((W, H))
    draw.polygon(hill_points, fill=NEAR_BLACK)

    # Red glow at base of center cross
    create_radial_gradient(img, (W // 2, H - 100), 300, BURGUNDY, NEAR_BLACK)

    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    img.save(os.path.join(IMAGE_DIR, "slide6_cross_death.jpg"), "JPEG", quality=95)
    print("  Generated: slide6_cross_death.jpg")


# ============================================================
# SLIDE 7: Five Descending Movements
# ============================================================
def generate_slide7_descending():
    """Dramatic descending staircase / pathway with light."""
    img = Image.new("RGB", (W, H), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Rich teal to deep purple gradient
    create_gradient(draw, W, H, DEEP_TEAL, DEEP_PURPLE)

    # Descending steps from upper-left to lower-right
    num_steps = 5
    step_w = 200
    step_h = 120
    x_start = 200
    y_start = 80

    for i in range(num_steps):
        x = x_start + i * (step_w + 40)
        y = y_start + i * step_h

        # Step platform with 3D effect
        t = i / (num_steps - 1)
        base_color = lerp_color(LIGHT_GOLD, BURGUNDY, t)
        dark_face = lerp_color(base_color, NEAR_BLACK, 0.5)
        highlight = lerp_color(base_color, WARM_WHITE, 0.3)

        # Top face
        top_points = [
            (x, y),
            (x + step_w, y),
            (x + step_w + 30, y + 20),
            (x + 30, y + 20),
        ]
        draw.polygon(top_points, fill=highlight)

        # Front face
        front_points = [
            (x + 30, y + 20),
            (x + step_w + 30, y + 20),
            (x + step_w + 30, y + 70),
            (x + 30, y + 70),
        ]
        draw.polygon(front_points, fill=base_color)

        # Side face
        side_points = [
            (x, y),
            (x + 30, y + 20),
            (x + 30, y + 70),
            (x, y + 50),
        ]
        draw.polygon(side_points, fill=dark_face)

        # Step number
        num_y = y + 30
        num_x = x + step_w // 2 + 15
        # Circle behind number
        for r in range(25, 0, -1):
            circle_t = r / 25
            cc = lerp_color(WARM_WHITE, base_color, circle_t)
            draw.ellipse([num_x - r, num_y - r, num_x + r, num_y + r], fill=cc)

    # Arrow suggesting downward movement
    arrow_points = [
        (W // 2, H - 180),
        (W // 2 - 60, H - 260),
        (W // 2 - 25, H - 260),
        (W // 2 - 25, H - 380),
        (W // 2 + 25, H - 380),
        (W // 2 + 25, H - 260),
        (W // 2 + 60, H - 260),
    ]
    # Gold arrow with glow
    for g in range(8, 0, -1):
        glow_pts = [(x + random.gauss(0, g), y + random.gauss(0, g)) for x, y in arrow_points]
        gc = lerp_color(GOLD, NEAR_BLACK, g / 8)
        draw.polygon(glow_pts, fill=gc)
    draw.polygon(arrow_points, fill=GOLD)

    # Particle trail along steps
    random.seed(100)
    for _ in range(200):
        i = random.random() * 4
        x = x_start + i * (step_w + 40) + random.gauss(step_w // 2, 50)
        y = y_start + i * step_h + random.gauss(30, 20)
        size = random.choice([1, 1, 2])
        color = lerp_color(LIGHT_GOLD, WARM_WHITE, random.random())
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)

    img = add_bokeh(img, count=10, min_r=15, max_r=45)
    img.save(os.path.join(IMAGE_DIR, "slide7_descending.jpg"), "JPEG", quality=95)
    print("  Generated: slide7_descending.jpg")


# ============================================================
# SLIDE 8: Pattern for Our Lives - Serving hands
# ============================================================
def generate_slide8_serving_hands():
    """Hands reaching out / offering light - service imagery."""
    img = Image.new("RGB", (W, H), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Warm gradient
    create_gradient(draw, W, H, DARK_BURGUNDY, DEEP_PURPLE)

    # Central warm glow (where hands meet)
    create_radial_gradient(img, (W // 2, H // 2), 500, LIGHT_GOLD, DEEP_PURPLE)
    draw = ImageDraw.Draw(img)

    # Stylized open hands (two hands reaching toward center)
    # Left hand - simplified elegant outline
    left_hand_cx = W // 2 - 200
    hand_y = H // 2

    # Simple elegant hand shapes using curves
    # Left hand (palm up, reaching right)
    left_palm = [
        (left_hand_cx - 100, hand_y + 20),
        (left_hand_cx - 80, hand_y - 30),
        (left_hand_cx - 40, hand_y - 50),
        (left_hand_cx, hand_y - 55),
        (left_hand_cx + 40, hand_y - 45),
        (left_hand_cx + 70, hand_y - 20),
        (left_hand_cx + 80, hand_y + 10),
        (left_hand_cx + 60, hand_y + 40),
        (left_hand_cx, hand_y + 50),
        (left_hand_cx - 60, hand_y + 45),
    ]
    # Draw with warm skin-like tone
    draw.polygon(left_palm, fill=(140, 90, 60), outline=GOLD)

    # Fingers (simplified as lines from palm)
    finger_starts = [
        (left_hand_cx - 50, hand_y - 40),
        (left_hand_cx - 20, hand_y - 52),
        (left_hand_cx + 10, hand_y - 55),
        (left_hand_cx + 40, hand_y - 45),
    ]
    finger_ends = [
        (left_hand_cx - 70, hand_y - 90),
        (left_hand_cx - 25, hand_y - 110),
        (left_hand_cx + 15, hand_y - 105),
        (left_hand_cx + 55, hand_y - 85),
    ]
    for start, end in zip(finger_starts, finger_ends):
        draw.line([start, end], fill=(140, 90, 60), width=12)
        draw.ellipse([end[0] - 6, end[1] - 6, end[0] + 6, end[1] + 6], fill=(140, 90, 60))

    # Right hand (mirror)
    right_hand_cx = W // 2 + 200
    right_palm = [
        (right_hand_cx + 100, hand_y + 20),
        (right_hand_cx + 80, hand_y - 30),
        (right_hand_cx + 40, hand_y - 50),
        (right_hand_cx, hand_y - 55),
        (right_hand_cx - 40, hand_y - 45),
        (right_hand_cx - 70, hand_y - 20),
        (right_hand_cx - 80, hand_y + 10),
        (right_hand_cx - 60, hand_y + 40),
        (right_hand_cx, hand_y + 50),
        (right_hand_cx + 60, hand_y + 45),
    ]
    draw.polygon(right_palm, fill=(140, 90, 60), outline=GOLD)

    r_finger_starts = [
        (right_hand_cx + 50, hand_y - 40),
        (right_hand_cx + 20, hand_y - 52),
        (right_hand_cx - 10, hand_y - 55),
        (right_hand_cx - 40, hand_y - 45),
    ]
    r_finger_ends = [
        (right_hand_cx + 70, hand_y - 90),
        (right_hand_cx + 25, hand_y - 110),
        (right_hand_cx - 15, hand_y - 105),
        (right_hand_cx - 55, hand_y - 85),
    ]
    for start, end in zip(r_finger_starts, r_finger_ends):
        draw.line([start, end], fill=(140, 90, 60), width=12)
        draw.ellipse([end[0] - 6, end[1] - 6, end[0] + 6, end[1] + 6], fill=(140, 90, 60))

    # Golden light/orb between hands
    orb_cx, orb_cy = W // 2, hand_y
    for r in range(80, 0, -1):
        t = r / 80
        color = lerp_color(WARM_WHITE, LIGHT_GOLD, t)
        draw.ellipse([orb_cx - r, orb_cy - r, orb_cx + r, orb_cy + r], fill=color)

    # Light particles emanating from orb
    random.seed(55)
    for _ in range(150):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.gauss(100, 60)
        x = orb_cx + math.cos(angle) * dist
        y = orb_cy + math.sin(angle) * dist
        size = random.choice([1, 1, 2, 2, 3])
        brightness = max(0, 1 - abs(dist) / 250)
        color = lerp_color(LIGHT_GOLD, WARM_WHITE, brightness)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)

    img = add_bokeh(img, count=10, min_r=20, max_r=50)
    img.save(os.path.join(IMAGE_DIR, "slide8_serving_hands.jpg"), "JPEG", quality=95)
    print("  Generated: slide8_serving_hands.jpg")


# ============================================================
# SLIDE 9: This Week's Challenge - Contemplation
# ============================================================
def generate_slide9_contemplating():
    """Person silhouette at crossroads / fork in the path with light."""
    img = Image.new("RGB", (W, H), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Gradient: dark purple to deep teal
    create_gradient(draw, W, H, DEEP_PURPLE, DARK_TEAL)

    # Two diverging paths
    # Path 1 (worldly - dimmer, going left)
    for i in range(200):
        t = i / 200
        x_center = W // 2 - t * 400
        y = H - 50 - t * (H - 200)
        width = 120 * (1 - t * 0.7)
        color = lerp_color((60, 40, 50), NEAR_BLACK, t)
        draw.line([(x_center - width / 2, y), (x_center + width / 2, y)], fill=color, width=2)

    # Path 2 (cross path - golden, going right)
    for i in range(200):
        t = i / 200
        x_center = W // 2 + t * 300
        y = H - 50 - t * (H - 200)
        width = 120 * (1 - t * 0.6)
        color = lerp_color(GOLD, DEEP_PURPLE, t * 0.8)
        draw.line([(x_center - width / 2, y), (x_center + width / 2, y)], fill=color, width=2)

    # Small cross at end of golden path
    cross_x = W // 2 + 280
    cross_y = 150
    for r in range(60, 0, -2):
        tc = r / 60
        cc = lerp_color(LIGHT_GOLD, DEEP_PURPLE, tc)
        draw.ellipse([cross_x - r, cross_y - r, cross_x + r, cross_y + r], fill=cc)
    draw_cross(draw, cross_x, cross_y, 80, 6, WARM_WHITE, glow=False)

    # Person silhouette at fork (center bottom)
    person_cx = W // 2
    person_base = H - 100

    # Head
    head_r = 18
    draw.ellipse([person_cx - head_r, person_base - 160 - head_r,
                  person_cx + head_r, person_base - 160 + head_r], fill=NEAR_BLACK)

    # Body
    draw.line([(person_cx, person_base - 142), (person_cx, person_base - 60)],
              fill=NEAR_BLACK, width=8)
    # Arms (slightly raised, contemplating)
    draw.line([(person_cx, person_base - 120), (person_cx - 40, person_base - 90)],
              fill=NEAR_BLACK, width=6)
    draw.line([(person_cx, person_base - 120), (person_cx + 40, person_base - 90)],
              fill=NEAR_BLACK, width=6)
    # Legs
    draw.line([(person_cx, person_base - 60), (person_cx - 25, person_base)],
              fill=NEAR_BLACK, width=6)
    draw.line([(person_cx, person_base - 60), (person_cx + 25, person_base)],
              fill=NEAR_BLACK, width=6)

    # Question mark made of light particles (upper area)
    qm_cx = W // 2 - 50
    qm_cy = H // 3

    # Draw question mark with golden dots
    qm_points = []
    # Curve of the ?
    for i in range(30):
        angle = math.pi * 1.5 - (i / 30) * math.pi * 1.2
        r = 60
        x = qm_cx + math.cos(angle) * r
        y = qm_cy - 40 + math.sin(angle) * r * 0.8
        qm_points.append((x, y))
    # Straight part down
    for i in range(8):
        x = qm_cx
        y = qm_cy + 20 + i * 5
        qm_points.append((x, y))

    for px, py in qm_points:
        for gr in range(6, 0, -1):
            gc = lerp_color(LIGHT_GOLD, DEEP_PURPLE, gr / 6)
            draw.ellipse([px - gr, py - gr, px + gr, py + gr], fill=gc)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=WARM_WHITE)

    # Dot of question mark
    dot_y = qm_cy + 70
    for gr in range(8, 0, -1):
        gc = lerp_color(LIGHT_GOLD, DEEP_PURPLE, gr / 8)
        draw.ellipse([qm_cx - gr, dot_y - gr, qm_cx + gr, dot_y + gr], fill=gc)
    draw.ellipse([qm_cx - 3, dot_y - 3, qm_cx + 3, dot_y + 3], fill=WARM_WHITE)

    # Ground
    for y in range(H - 60, H):
        t = (y - H + 60) / 60
        color = lerp_color(DARK_TEAL, NEAR_BLACK, t)
        draw.line([(0, y), (W, y)], fill=color)

    add_stars(draw, count=80, region=(0, 0, W, H // 2))
    img = add_bokeh(img, count=6, min_r=15, max_r=35)
    img.save(os.path.join(IMAGE_DIR, "slide9_contemplating.jpg"), "JPEG", quality=95)
    print("  Generated: slide9_contemplating.jpg")


# ============================================================
# MAIN
# ============================================================
def main():
    print("Generating custom artwork for Bible class presentation...")
    print("Color palette: Deep Purple, Burgundy, Gold, Deep Teal\n")

    generate_slide2_cross_mindset()
    generate_slide3_incarnation()
    generate_slide4_emptying()
    generate_slide5_humble()
    generate_slide6_cross_death()
    generate_slide7_descending()
    generate_slide8_serving_hands()
    generate_slide9_contemplating()

    print("\nAll images generated successfully!")
    print(f"Output directory: {IMAGE_DIR}")

    # Verify all files
    for f in sorted(os.listdir(IMAGE_DIR)):
        path = os.path.join(IMAGE_DIR, f)
        size = os.path.getsize(path)
        print(f"  {f}: {size:,} bytes")


if __name__ == "__main__":
    main()
