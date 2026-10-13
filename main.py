import asyncio
import pygame
import random
import math

# ---------------------------------------------------------
# Unit 2 - Lesson 4
# Velocity, Acceleration, Momentum, and Drag
#
# Controls:
# LEFT / A   = Rotate left
# RIGHT / D  = Rotate right
# UP / W     = Apply thrust
# SPACE      = Fire missile
#
# Main Idea:
# Direction -> Acceleration -> Velocity -> Position
# ---------------------------------------------------------

pygame.init()

# =========================================================
# Game Constants
# =========================================================

WIDTH = 800
HEIGHT = 800
FPS = 60

NUM_ASTEROIDS = 3

ROTATION_SPEED = 3

# Lesson 4 Physics Constants
THRUST = 0.15
DRAG = 0.99
MAX_SPEED = 7

MISSILE_SPEED = 8

# Colors
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
GREEN = (80, 255, 150)
YELLOW = (255, 230, 80)
RED = (255, 80, 80)
BLUE = (80, 180, 255)
ORANGE = (255, 140, 50)


# =========================================================
# Pygame Setup
# =========================================================

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption(
    "Lesson 4 - Velocity, Acceleration, Momentum, and Drag"
)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 25)

# =========================================================
# Spaceship Class
# =========================================================

class Spaceship:
    def __init__(self, x, y):
        # Position tells us WHERE the ship is.
        self.position = pygame.Vector2(x, y)

        # Velocity tells us HOW the ship is moving.
        self.velocity = pygame.Vector2(0, 0)

        # Acceleration tells us HOW velocity is changing.
        self.acceleration = pygame.Vector2(0, 0)

        # Start facing upward.
        self.angle = 90
        self.radius = 18
        self.is_thrusting = False
        self.invincible_time = 0 

    # -----------------------------------------------------
    # Convert Angle -> Forward Direction Vector
    # Lesson 3 Review
    # -----------------------------------------------------

    def get_forward_vector(self):
        radians = math.radians(self.angle)
        forward = pygame.Vector2(
                math.cos(radians),
                -math.sin(radians)
        )
        return forward

    # -----------------------------------------------------
    # Update Spaceship
    # -----------------------------------------------------

    def update(self):
        keys = pygame.key.get_pressed()
        if self.invincible_time > 0:
            self.invincible_time -= 1

        # -------------------------------------------------
        # Rotation
        # -------------------------------------------------

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle += ROTATION_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angle -= ROTATION_SPEED
        # -------------------------------------------------
        # Calculate Forward Direction
        # -------------------------------------------------

        forward = self.get_forward_vector()

        # -------------------------------------------------
        # LESSON 4:
        # Reset acceleration every frame.
        #
        # The engine should only accelerate the ship
        # while the thrust key is being pressed.
        # -------------------------------------------------

        self.acceleration = pygame.Vector2(0, 0)
        self.is_thrusting = False

        # -------------------------------------------------
        # Apply Thrust
        #
        # We are NOT directly changing position.
        #
        # Instead:
        #
        # forward direction * thrust
        # -> acceleration
        # -------------------------------------------------
        if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.acceleration = forward * THRUST
                self.is_thrusting = True

        # -------------------------------------------------
        # LESSON 4 PHYSICS
        #
        # Acceleration changes velocity.
        # -------------------------------------------------

        self.velocity += self.acceleration

        # -------------------------------------------------
        # Apply Drag
        #
        # Drag gradually reduces the magnitude
        # of the velocity vector.
        # -------------------------------------------------

        self.velocity *= DRAG

        # -------------------------------------------------
        # Limit Maximum Speed
        # -------------------------------------------------

        if self.velocity.length() > MAX_SPEED:
                self.velocity.scale_to_length(MAX_SPEED)

        # -------------------------------------------------
        # Velocity changes position.
        # -------------------------------------------------

        self.position += self.velocity

        # -------------------------------------------------
        # Screen Wrapping
        # -------------------------------------------------

        if self.position.x > WIDTH:
                self.position.x = 0

        if self.position.x < 0:
                self.position.x = WIDTH

        if self.position.y > HEIGHT:
                self.position.y = 0

        if self.position.y < 0:
                self.position.y = HEIGHT

    # -----------------------------------------------------
    # Draw Spaceship
    # -----------------------------------------------------

    def draw(self):
        forward = self.get_forward_vector()
        if self.invincible_time > 0 and (self.invincible_time // 4) % 2 == 0:
            return
        # Rotate the forward vector to make
        # the other two corners of the ship.
        left = forward.rotate(140)
        right = forward.rotate(-140)

        # Triangle points
        front = self.position + forward * 22
        back_left = self.position + left * 17
        back_right = self.position + right * 17

        pygame.draw.polygon(
                screen,
                GREEN,
                [front, back_left, back_right],
                2
        )

        # Center point
        pygame.draw.circle(
                screen,
                GREEN,
                (int(self.position.x), int(self.position.y)),
                3
        )

        # -------------------------------------------------
        # Draw Engine Flame While Burning
        # -------------------------------------------------

        if self.is_thrusting:
                flame_position = (
                    self.position - forward * 20
                )
                pygame.draw.circle(
                    screen,
                    ORANGE,
                    (
                        int(flame_position.x),
                        int(flame_position.y)
                    ),
                    5
                )

    # -----------------------------------------------------
    # Draw Forward Vector
    #
    # RED = direction the ship is FACING
    # -----------------------------------------------------

    def draw_forward_vector(self):
        forward = self.get_forward_vector()
        end_point = (
                self.position + forward * 60
        )
        pygame.draw.line(
                screen,
                RED,
                self.position,
                end_point,
                2
        )

    # -----------------------------------------------------
    # Draw Velocity Vector
    #
    # BLUE = direction the ship is MOVING
    # -----------------------------------------------------

    def draw_velocity_vector(self):
        # Only draw if the ship is moving.
        if self.velocity.length() > 0.1:
                end_point = (
                    self.position
                    + self.velocity * 10
                )
                pygame.draw.line(
                    screen,
                    BLUE,
                    self.position,
                    end_point,
                    3
                )

# =========================================================
# Asteroid Class
# =========================================================

class Asteroid:
    def __init__(self):
        self.radius = random.randint(18, 35)
        self.position = pygame.Vector2(
                random.randint(
                    self.radius,
                    WIDTH - self.radius
                ),
                random.randint(
                    self.radius,
                    HEIGHT - self.radius
                )
        )

        # Random direction
        angle = random.uniform(
                0,
                2 * math.pi
        )

        # Random speed
        speed = random.uniform(
                1.0,
                2.5
        )

        self.velocity = pygame.Vector2(
                math.cos(angle),
                math.sin(angle)
        ) * speed

    def update(self):
        # Lesson 1:
        # Position changes by velocity.
        self.position += self.velocity

        # Screen wrapping
        if self.position.x > WIDTH + self.radius:
                self.position.x = -self.radius

        if self.position.x < -self.radius:
                self.position.x = WIDTH + self.radius

        if self.position.y > HEIGHT + self.radius:
                self.position.y = -self.radius

        if self.position.y < -self.radius:
                self.position.y = HEIGHT + self.radius

    def draw(self):
        pygame.draw.circle(
                screen,
                GRAY,
                (
                    int(self.position.x),
                    int(self.position.y)
                ),
                self.radius,
                2
        )

# =========================================================
# Missile Class
# =========================================================

class Missile:
    def __init__(self, start_position, direction):
        self.position = pygame.Vector2(
                start_position
        )

        self.radius = 4

        # Direction * Speed = Velocity
        self.velocity = (
                direction * MISSILE_SPEED
        )

    def update(self):
        self.position += self.velocity

    def draw(self):
        pygame.draw.circle(
                screen,
                YELLOW,
                (
                    int(self.position.x),
                    int(self.position.y)
                ),
                self.radius
        )

    def is_off_screen(self):
        return (
                self.position.x < 0
                or self.position.x > WIDTH
                or self.position.y < 0
                or self.position.y > HEIGHT
        )

# =========================================================
# Enemy Class
# =========================================================

class Enemy:
    # Class variables (Shared by all enemies)
    DETECTION_RANGE = 300
    FOV_THRESHOLD = 0.7
    FIRE_COOLDOWN = 3000

    def __init__(self, x, y):
        self.position = pygame.Vector2(
                x,
                y
        )
        self.velocity = pygame.Vector2(0, 0)
        self.angle = 0
        self.last_shot_time = 0
        self.speed = 1
        self.acceleration = 0.1
        self.drag = 0.99
        self.rotation_speed = 1
        self.radius = 18


    def get_forward_vector(self):
        radians = math.radians(self.angle)
        enemy_forward = pygame.Vector2(
                math.cos(radians),
                -math.sin(radians)
        )
        return enemy_forward

    def update(self, player):
        if detection(player, self):
            direction = player.position - self.position

            if direction.length() > 0:
                direction = direction.normalize()
                self.position += direction * self.speed
                target_angle = math.degrees(
                    math.atan2(-direction.y, direction.x)
                )
                angle_difference = (
                    target_angle - self.angle + 180
                ) % 360 - 180
                if abs(angle_difference) < self.rotation_speed:
                    self.angle = target_angle
                else:
                    self.angle += (
                        self.rotation_speed
                        if angle_difference > 0
                        else -self.rotation_speed
                    )
                if abs(angle_difference) < 45:
                    forward = self.get_forward_vector()
                    self.velocity += forward * self.acceleration
            self.velocity *= self.drag

            if self.velocity.length() > self.speed:
                self.velocity.scale_to_length(self.speed)

            self.position += self.velocity

            self.respond(player)
        else:
            self.angle += self.rotation_speed
            self.velocity *= self.drag
            self.position += self.velocity

    def draw(self, player):
        # Draw Detection Circle
        pygame.draw.circle(
            screen,
            GRAY,
            self.position,
            self.DETECTION_RANGE,
            1
        )
        # Draw Enemy Ship
        if detection(player, self):
                self.rotate_to_player(player)
                forward = self.get_forward_vector()
                left = forward.rotate(140)
                right = forward.rotate(-140)
                front = self.position + forward * 22
                back_left = self.position + left * 17
                back_right = self.position + right * 17
                pygame.draw.polygon(
                    screen,
                    RED,
                    [front, back_left, back_right],
                    2
                )
                pygame.draw.circle(
                    screen,
                    RED,
                    self.position,
                    5
                )
        else:
                forward = self.get_forward_vector()
                left = forward.rotate(140)
                right = forward.rotate(-140)
                front = self.position + forward * 22
                back_left = self.position + left * 17
                back_right = self.position + right * 17
                pygame.draw.polygon(
                    screen,
                    GRAY,
                    [front, back_left, back_right],
                    2
                )
                pygame.draw.circle(
                    screen,
                    GRAY,
                    self.position,
                    5
                )

    def draw_forward_vector(self):
        forward = self.get_forward_vector()
        pygame.draw.line(
                screen,
                RED,
                self.position,
                self.position + forward * 100,
                3
        )

    def rotate_to_player(self, player):
        direction = player.position - self.position
        if direction.length() > 0:
            radians = math.atan2(-direction.y, direction.x)
            self.angle = math.degrees(radians)

    def respond(self, player):
        forward = self.get_forward_vector()
        current_time = pygame.time.get_ticks()

        if detection(player, self):
            self.angle
            direction = (
                player.position - self.position
            ).normalize()
            if current_time - self.last_shot_time >= self.FIRE_COOLDOWN:
                missile_velocity = (
                    direction * MISSILE_SPEED
                )
                missile_start = (
                    self.position
                    + forward * 24
                )
                new_missile = Missile(
                    missile_start,
                    forward
                )
                missiles.append(
                    new_missile
                )
                self.last_shot_time = current_time
            else:
                pass

# =========================================================
# Player Detection
# =========================================================

def detection(player, enemy):
    forward = enemy.get_forward_vector()
    to_player = (
        player.position - enemy.position
    )
    if to_player.length() > 0:
        to_player = to_player.normalize()
    distance = enemy.position.distance_to(
        player.position
    )
    dot = enemy.get_forward_vector().dot(
        to_player
    )

    if (
        distance < enemy.DETECTION_RANGE
        and dot > enemy.FOV_THRESHOLD
    ):
        detected = True

    else:
        detected = False
    return detected

# =========================================================
# Functions
# =========================================================

def missile_hits_asteroid(
    missile,
    asteroid
):
    distance = (
        missile.position.distance_to(
                asteroid.position
        )
    )

    return (
        distance
        < missile.radius + asteroid.radius
    )

# My work
def asteroid_hits_player(
    asteroid,
    player
):
        distance = (
                (asteroid.position - player.position).length()
        )
        return distance < asteroid.radius

def missile_hits_player(
    missile,
    player
):
        distance = (
                (missile.position - player.position).length()
        )
        return distance < missile.radius + player.radius

def missile_hits_enemy(
    missile,
    enemy
):
        distance = (
                (missile.position - enemy.position).length()
        )
        return distance < missile.radius + enemy.radius

# =========================================================
# Create Game Objects
# =========================================================

player = Spaceship(
    WIDTH / 2,
    HEIGHT / 2
)

enemy = Enemy(
    WIDTH / 4,
    HEIGHT / 2
)

asteroids = []

for i in range(NUM_ASTEROIDS):
    asteroids.append(
        Asteroid()
    )

missiles = []
score = 0

# =========================================================
# Async Game Functions
# =========================================================

async def game_over_screen():
    global score, missiles, asteroids
    score -= 10
    
    player.position = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    player.velocity = pygame.Vector2(0, 0)
    player.acceleration = pygame.Vector2(0, 0)
    
    missiles.clear()
    asteroids.clear()
    game_over_screen_active = True
    
    while game_over_screen_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_over_screen_active = False

        screen.fill(BLACK)
        game_over_text = font.render(
            "Player Hit! Score -10! Enter to continue",
            True,
            WHITE
        )
        screen.blit(
            game_over_text,
            (WIDTH / 2 - game_over_text.get_width() / 2, HEIGHT / 2)
        )
        pygame.display.flip()
        clock.tick(FPS)
        
        await asyncio.sleep(0)

    for i in range(NUM_ASTEROIDS):
        asteroids.append(Asteroid())
    pygame.event.clear()

async def main():
    global score, missiles, asteroids, player, enemy
    # =========================================================
    # Main Game Loop
    # =========================================================

    running = True
    while running:
        # =====================================================
        # 1. EVENT HANDLING
        # =====================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    running = False

            # -------------------------------------------------
            # Fire Missile
            # -------------------------------------------------

            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Missile fires in the direction
                        # the spaceship is facing.
                        forward = (
                            player.get_forward_vector()
                        )
                        missile_start = (
                            player.position
                            + forward * 24
                        )
                        new_missile = Missile(
                            missile_start,
                            forward
                        )
                        missiles.append(
                            new_missile
                        )

        # =====================================================
        # 2. UPDATE PLAYER & ENEMY
        # =====================================================

        player.update()
        enemy.update(player)

        # =====================================================
        # 3. UPDATE ASTEROIDS
        # =====================================================

        for asteroid in asteroids:
            asteroid.update()

        # =====================================================
        # 4. UPDATE MISSILES
        # =====================================================

        for missile in missiles:
            missile.update()

        # =====================================================
        # 5. REMOVE OFF-SCREEN MISSILES
        # =====================================================

        missiles = [
            missile
            for missile in missiles
            if not missile.is_off_screen()
        ]

        # =====================================================
        # 6. MISSILE / ASTEROID COLLISION
        # =====================================================

        for missile in missiles[:]:
            for asteroid in asteroids[:]:
                    if missile_hits_asteroid(
                        missile,
                        asteroid
                    ):
                        if missile in missiles:
                            missiles.remove(
                                    missile
                            )
                        if asteroid in asteroids:
                            asteroids.remove(
                                    asteroid
                            )
                        # Replace destroyed asteroid
                        asteroids.append(
                            Asteroid()
                        )
                        score += 1
                        break

        # =====================================================
        # 6.5. ASTEROID ASTEROID COLLISION
        # =====================================================

        for i in range(len(asteroids)):
            for j in range(i + 1, len(asteroids)):
                    a1 = asteroids[i]
                    a2 = asteroids[j]

                    # Distance
                    dist_vec = a2.position - a1.position
                    distance = dist_vec.length()
                    min_dist = a1.radius + a2.radius

                    if distance < min_dist:
                        # If overlap then skip
                        if distance == 0:
                            continue

                        # Fix overlap
                        overlap = min_dist - distance
                        normal = dist_vec.normalize()
                        a1.position -= normal * (overlap * 0.5)
                        a2.position += normal * (overlap * 0.5)

                        # This is the collision math
                        # the velocity on their direct path
                        rel_vel = a2.velocity - a1.velocity
                        vel_along_normal = rel_vel.dot(normal)

                        # 2v/m1+m2
                        if vel_along_normal < 0:
                            impulse = (2 * vel_along_normal) / (a1.radius**2 + a2.radius**2)

                            a1.velocity += normal * impulse * a2.radius**2
                            a2.velocity -= normal * impulse * a1.radius**2
        # =====================================================
        # 6.75. ASTEROID PLAYER COLLISION
        # =====================================================

        for asteroid in asteroids:
            if asteroid_hits_player(
                asteroid, player
                ):
                print("asteroid_hits_player!")
                await game_over_screen()

        # =====================================================
        # 6.8. MISSILE PLAYER COLLISION
        # =====================================================

        for missile in missiles:
            if missile_hits_player(
                missile, player
                ):
                print("missile_hits_player!")
                await game_over_screen()

        # =====================================================
        # 6.85. MISSILE ENEMY COLLISION
        # =====================================================

        for missile in missiles:
            if missile_hits_enemy(
                missile, enemy
                ):
                print("missile_hits_enemy!")
                score += 5

        # =====================================================
        # 7. DRAW EVERYTHING
        # =====================================================

        screen.fill(BLACK)

        # Draw asteroids
        for asteroid in asteroids:
            asteroid.draw()

        # Draw missiles
        for missile in missiles:
            missile.draw()

        # -----------------------------------------------------
        # Draw vectors BEFORE ship
        # -----------------------------------------------------

        # RED = where ship is facing
        player.draw_forward_vector()

        # BLUE = where ship is actually moving
        player.draw_velocity_vector()

        # Draw spaceship
        player.draw()

        enemy.draw_forward_vector()
        enemy.draw(player)

        # =====================================================
        # 8. DISPLAY INFORMATION
        # =====================================================

        forward = (
            player.get_forward_vector()
        )

        speed = (
            player.velocity.length()
        )

        # -----------------------------------------------------
        # Controls
        # -----------------------------------------------------

        controls_text = font.render(
            "LEFT/RIGHT: Rotate   UP: Thrust   SPACE: Fire",
            True,
            WHITE
        )

        screen.blit(
            controls_text,
            (20, 15)
        )

        # -----------------------------------------------------
        # Angle
        # -----------------------------------------------------

        angle_text = font.render(
            f"Angle: {player.angle % 360:.0f} degrees",
            True,
            WHITE
        )

        screen.blit(
            angle_text,
            (20, 45)
        )

        # -----------------------------------------------------
        # Forward Vector
        # -----------------------------------------------------

        forward_text = font.render(
            f"Forward: ({forward.x:.2f}, {forward.y:.2f})",
            True,
            RED
        )
        screen.blit(
            forward_text,
            (20, 75)
        )

        # -----------------------------------------------------
        # Velocity Vector
        # -----------------------------------------------------

        velocity_text = font.render(
            f"Velocity: ({player.velocity.x:.2f}, "
            f"{player.velocity.y:.2f})",
            True,
            BLUE
        )
        screen.blit(
            velocity_text,
            (20, 105)
        )

        # -----------------------------------------------------
        # Speed
        # -----------------------------------------------------

        speed_text = font.render(
            f"Speed: {speed:.2f}",
            True,
            WHITE
        )
        screen.blit(
            speed_text,
            (20, 135)
        )

        # -----------------------------------------------------
        # Acceleration
        # -----------------------------------------------------

        acceleration_text = font.render(
            f"Acceleration: "
            f"({player.acceleration.x:.2f}, "
            f"{player.acceleration.y:.2f})",
            True,
            WHITE
        )
        screen.blit(
            acceleration_text,
            (20, 165)
        )

        # -----------------------------------------------------
        # Score
        # -----------------------------------------------------

        score_text = font.render(
            f"Score: {score}",
            True,
            WHITE
        )
        screen.blit(
            score_text,
            (20, 195)
        )

        # -----------------------------------------------------
        # Vector Legend
        # -----------------------------------------------------

        legend_text = font.render(
            "RED = Facing Direction     BLUE = Velocity    \n"
            "SCORE = Asteroid Hits (+1) / Enemy Hits (+5) / Player Hit (-10)",
            True,
            WHITE
        )

        screen.blit(
            legend_text,
            (20, HEIGHT - 65)
        )

        # -----------------------------------------------------
        # Main Lesson Formula
        # -----------------------------------------------------

        formula_text = font.render(
            "Acceleration -> Velocity -> Position",
            True,
            GREEN
        )

        screen.blit(
            formula_text,
            (20, HEIGHT - 35)
        )

        pygame.display.flip()
        clock.tick(60) 
        await asyncio.sleep(0) 

    pygame.quit()

asyncio.run(main())
