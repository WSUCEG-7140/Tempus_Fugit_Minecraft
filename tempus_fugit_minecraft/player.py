from typing import Callable
from tempus_fugit_minecraft.world import World
from tempus_fugit_minecraft.block import Block
import math


class Player:
    """!
    @brief The Player class handles all attributes and functions concerning the player, including speed adjustments,
        player position, player sight vector, and more.
    @return player An instance of Player class.
    """
    def __init__(self) -> None:
        """!
        @brief Initializes an instance of the Player class
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.MAX_JUMP_HEIGHT_IN_BLOCKS = 1.0
        self.PLAYER_HEIGHT_IN_BLOCKS = 2
        self.MAX_FALL_SPEED_IN_BLOCKS_PER_SECOND = 50
        self.FLYING_SPEED_IN_BLOCKS_PER_SECOND = 15
        self.GRAVITY_IN_BLOCKS_PER_SECOND_SQUARED = 20.0
        self.MAX_SPEED_IN_BLOCKS_PER_SECOND = 15
        self.MIN_SPEED_IN_BLOCKS_PER_SECOND = 5

        # To derive the formula for calculating jump speed, first solve
        #    v_t = v_0 + a * t
        # for the time at which you achieve maximum height, where a is the acceleration
        # due to gravity and v_t = 0. This gives:
        #    t = - v_0 / a
        # Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
        #    s = s_0 + v_0 * t + (a * t^2) / 2
        self.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND = int(math.sqrt(2 * self.GRAVITY_IN_BLOCKS_PER_SECOND_SQUARED * self.MAX_JUMP_HEIGHT_IN_BLOCKS))
        self.MAX_JUMP_SPEED_IN_BLOCKS_PER_SECOND = self.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND + 10
        self.MIN_JUMP_SPEED_IN_BLOCKS_PER_SECOND = self.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND
        self.WALK_SPEED_IN_BLOCKS_PER_SECOND = 5

        self.jump_speed_in_blocks_per_second = self.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND
        self.walking_speed_in_blocks_per_second = self.WALK_SPEED_IN_BLOCKS_PER_SECOND
       
        # When flying gravity has no effect and speed is increased.
        self.flying = False
        self.ascend = False
        self.descend = False
        # Strafing is moving lateral to the direction you are facing, e.g. moving to the left or right while
        # continuing to face forward.

        # First element is -1 when moving forward, 1 when moving back, and 0 otherwise.
        # The second element is -1 when moving left, 1 when moving right, and 0 otherwise.
        self.strafe_unit_vector = [0, 0]
        # Current (x, y, z) position in the world, specified with floats. Note that, perhaps unlike in math class,
        # the y-axis is the vertical axis.
        self.position_in_blocks_from_origin = (0, 0, 0)
        # First element is rotation of the player in the x-z plane (ground plane) measured from the z-axis down. The
        # second is the rotation angle from the ground plane up. Rotation is in degrees.

        # The vertical plane rotation ranges from -90 (looking straight down) to 90 (looking straight up). The
        # horizontal rotation range is unbounded.
        self.rotation_in_degrees = (0, 0)
        # Velocity in the y (upward) direction.
        self.vertical_velocity_in_blocks_per_second = 0
        # A list of blocks the player can place. Hit num keys to cycle.
        self.inventory = [Block.BRICK, Block.GRASS, Block.SAND, Block.TREE_TRUNK, Block.TREE_LEAVES, Block.LIGHT_CLOUD, Block.DARK_CLOUD]
        # The current block the user can place. Hit num keys to cycle.
        self.selected_block = self.inventory[0]

    def get_sight_vector(self) -> tuple:
        """!
        @brief Returns the current line of sight vector indicating the direction the player is looking.
        @return A tuple representing the 3D vector the player is looking toward
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        x, y = self.rotation_in_degrees
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and is 1 when looking ahead parallel to
        # the ground and 0 when looking straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return dx, dy, dz

    def get_motion_vector(self) -> tuple:
        """!
        @brief Returns the current motion vector indicating the velocity of the player.
        @return A tuple containing the velocity in x, y, and z respectively.
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        if any(self.strafe_unit_vector):
            x, y = self.rotation_in_degrees
            strafe = math.degrees(math.atan2(*self.strafe_unit_vector))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe_unit_vector[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe_unit_vector[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz
 
    def increase_walk_speed(self) -> None:
        """!
        @brief Increases the walking speed of the player.
        @see [Issue#37](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/37)
        @see [Issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        @see [Issue#37](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/37)
        @see [Issue#71](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/71)

        """
        if self.walking_speed_in_blocks_per_second <= self.MAX_SPEED_IN_BLOCKS_PER_SECOND:
            self.walking_speed_in_blocks_per_second += self.WALK_SPEED_IN_BLOCKS_PER_SECOND
    
    def decrease_walk_speed(self) -> None:
        """!
        @brief Decreases the walking speed of the player
        @see [Issue#38](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/38)
        @see [Issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        @see [Issue#71](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/71)
        """
        if self.walking_speed_in_blocks_per_second > self.MIN_SPEED_IN_BLOCKS_PER_SECOND:
            self.walking_speed_in_blocks_per_second -= self.WALK_SPEED_IN_BLOCKS_PER_SECOND
   
    def increase_jump_speed(self) -> None:  
        """!
        @brief increase the jump speed of the player
        @see [issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        """     
        if self.jump_speed_in_blocks_per_second <= self.MAX_JUMP_SPEED_IN_BLOCKS_PER_SECOND: 
                self.jump_speed_in_blocks_per_second = self.jump_speed_in_blocks_per_second + 5
            
    def decrease_jump_speed(self) -> None:
        """!
        @brief decreases the jump speed of the player
        @see [issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        """
        if self.jump_speed_in_blocks_per_second > self.MIN_JUMP_SPEED_IN_BLOCKS_PER_SECOND:       
            self.jump_speed_in_blocks_per_second = self.jump_speed_in_blocks_per_second - 5

    def move_forward(self) -> None:
        """!
        @brief Move one space to the front
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe_unit_vector[0] -= 1

    def move_backward(self) -> None:
        """!
        @brief Move one space to the rear
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe_unit_vector[0] += 1

    def move_left(self) -> None:
        """!
        @brief Move one space to the left
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe_unit_vector[1] -= 1

    def move_right(self) -> None:
        """!
        @brief Move one space to the right
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe_unit_vector[1] += 1

    def jump(self) -> None:
        """!
        @brief If the user is grounded, jump
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        if self.vertical_velocity_in_blocks_per_second == 0:
            self.vertical_velocity_in_blocks_per_second = self.jump_speed_in_blocks_per_second

    def select_active_item(self, index: int) -> None:
        """!
        @brief Selects the active item in the player's inventory
        @param index The current index of the inventory
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        selected_index = index % len(self.inventory)
        self.selected_block = self.inventory[selected_index]

    def stop_forward(self) -> None:
        """!
        @brief Stops movement to the front
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe_unit_vector[0] += 1

    def stop_backward(self) -> None:
        """!
        @brief Stops movement to the rear
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe_unit_vector[0] -= 1

    def stop_left(self) -> None:
        """!
        @brief Stops movement to the left
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe_unit_vector[1] += 1

    def stop_right(self) -> None:
        """!
        @brief Stops movement to the right
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe_unit_vector[1] -= 1

    def adjust_sight(self, dx: int, dy: int) -> None:
        """!
        @brief Adjusts the sight vector of the player
        @param dx The relative x-axis movement of the mouse
        @param dy The relative y-axis movement of the mouse
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        x, y = self.rotation_in_degrees
        m = 0.15
        x = dx * m + x
        y = dy * m + y
        y = max(-90, min(90, y))
        self.rotation_in_degrees = (x, y)

    def current_speed(self) -> float:
        """!
        @brief Gets the current walking or flying speed
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        return self.FLYING_SPEED_IN_BLOCKS_PER_SECOND if self.flying else self.walking_speed_in_blocks_per_second

    def toggle_flight(self) -> None:
        """!
        @brief Toggles flight in game
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.flying = not self.flying

    def update(self, delta_time_in_seconds: float, collision_checker: Callable[[tuple, int], tuple]) -> None:
        """!
        @brief Private implementation of the `update()` method. This is where most of the motion logic lives,
            along with gravity and collision detection.
        @param delta_time_in_seconds The change in time (seconds) since the last call.
        @param collision_checker Takes in a new player position and the player height, then returns a new position
            adjusted for any potential block collisions
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        @see [Issue#82](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/82)
        """
        # walking
        speed = self.current_speed()
        d = delta_time_in_seconds * speed  # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d

        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up
            # until you hit terminal velocity; if you are jumping, slow
            # down until you start falling.
            self.vertical_velocity_in_blocks_per_second -= delta_time_in_seconds * self.GRAVITY_IN_BLOCKS_PER_SECOND_SQUARED
            self.vertical_velocity_in_blocks_per_second = max(self.vertical_velocity_in_blocks_per_second, -self.MAX_FALL_SPEED_IN_BLOCKS_PER_SECOND)
            dy += self.vertical_velocity_in_blocks_per_second * delta_time_in_seconds
        else:
            # The vertical_direction_modifier will either add or subtract one, or both, if
            # the ascending or descending properties are true, the
            # result of this will be -1, 0 or 1 which will change the
            # direction of dy.
            vertical_direction_modifier = 0
            vertical_direction_modifier += 1 if self.ascend else 0
            vertical_direction_modifier -= 1 if self.descend else 0
            dy += vertical_direction_modifier * delta_time_in_seconds * self.FLYING_SPEED_IN_BLOCKS_PER_SECOND

        # collisions
        x, y, z = self.position_in_blocks_from_origin
        self.position_in_blocks_from_origin = collision_checker((x + dx, y + dy, z + dz),  self.PLAYER_HEIGHT_IN_BLOCKS)

    def check_player_within_world_boundaries(self) -> None:
        """!
        @brief Ensure that the player character remains within the confines of the defined game world.
        @see [Issue#25](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/25)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        """
        x, y, z = self.position_in_blocks_from_origin

        x = self.keep_player_within_coordinates(x, boundary_size=World.WIDTH_FROM_ORIGIN_IN_BLOCKS)
        z = self.keep_player_within_coordinates(z, boundary_size=World.WIDTH_FROM_ORIGIN_IN_BLOCKS)
        self.position_in_blocks_from_origin = (x, y, z)

    @staticmethod
    def keep_player_within_coordinates(dimension, boundary_size=World.WIDTH_FROM_ORIGIN_IN_BLOCKS):
        """!
        @brief check whether the dimension (usually x or z) is within the boundary size.
        @param dimension represent a player dimension (x,y, or z)
        @param boundary_size represent the size of the world withing the walls.
        @return The dimension adjusted to be within the boundary size.
        @see [Issue#25](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/25)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        """
        if dimension > boundary_size:
            return boundary_size
        elif dimension < -boundary_size:
            return -boundary_size
        else:
            return dimension

    def slow_walking_speed(self) -> None:
        """!
        @brief Slows the player's walking speed
        @see [Issue#97](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/97)
        @see [Issue#115](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/115)
        """
        # Preconditions: make sure the initial speed = 5
        assert self.walking_speed_in_blocks_per_second == 5
        self.walking_speed_in_blocks_per_second = self.walking_speed_in_blocks_per_second / 3
        # Postconditions: make sure the speed decreased and it is = 5/3
        assert self.walking_speed_in_blocks_per_second == 5 / 3

    def reset_walking_speed(self) -> None:
        """!
        @brief Resets the player's walking speed to the default value
        @see [Issue#97](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/97)
        @see [Issue#98](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/98)
        """
        self.walking_speed_in_blocks_per_second = 5

    def start_sprinting(self) -> None:
        """!
        @brief Increases the player's walking speed
        @see [Issue#98](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/98)
        """
        self.walking_speed_in_blocks_per_second = self.walking_speed_in_blocks_per_second * 2
