from unittest.mock import Mock

import pyglet

from tempus_fugit_minecraft.main import Model, Window, LIGHT_CLOUD, DARK_CLOUD


class TestSpeed:
    def test_speed_up(self):
        window = Window()
        assert window.walking_speed == 5

        window.speed_up()
        assert window.walking_speed == 10

        window.speed_up()
        assert window.walking_speed == 15

        for _ in range(0,9):
            window.speed_up()
        assert window.walking_speed == 20  # 20 is the max speed
    
    def test_up_key(self):
        window = Window()
        assert window.walking_speed == 5

        window.on_key_press(pyglet.window.key.UP, Mock())
        assert window.walking_speed == 10


class TestClouds:
    def test_light_clouds_created_dynamically(self):
        model = Model()
        model.generate_clouds_positions(80, 100)
        count_clouds = sum(1 for block in model.world.values() if block == LIGHT_CLOUD)
        
        assert  count_clouds >= 1, "LIGHT_CLOUD was not identified"

    def test_cloud_positions(self):
        model = Model()
        model.generate_clouds_positions(80, 100)
        o = 80 + 2*6        # + 2*6 to insure that the test will cover cloud block outside the world.
        cloud_blocks = [coord for coord, block in model.world.items() if block in [LIGHT_CLOUD,DARK_CLOUD]]
        for block in cloud_blocks:
            assert -o <= block[0] <= o
            assert -o <= block[2] <= o

    def test_cloud_height(self):
        model = Model()
        model.generate_clouds_positions(80, 100)
        clouds = [coord for coord, block in model.world.items() if block in [LIGHT_CLOUD,DARK_CLOUD]]
        for cloud_coordinates in clouds:
            assert cloud_coordinates[1] >= 20

    def test_non_overlapping_clouds(self):
        model = Model()
        model.generate_clouds_positions(80, 100)
        blocks_of_all_clouds = [coordinates for coordinates , block in model.world.items() if block in [LIGHT_CLOUD,DARK_CLOUD]]
        unique_clouds = set(blocks_of_all_clouds)
        assert len(blocks_of_all_clouds) == len(unique_clouds)
    
    def test_dark_clouds_created_dynamically(self):
        model = Model()
        model.generate_clouds_positions(80,200)
        count_dark_cloud_blocks = sum(1 for block in model.world.values() if block == DARK_CLOUD)
        assert count_dark_cloud_blocks >= 1, "DARK_CLOUDs were not identified"
    
    def test_draw_clouds_in_the_sky_and_count_blocks(self):
        model = Model()
        clouds = model.generate_clouds_positions(80,150)
        model.place_cloud_blocks(clouds)
        cloud_blocks = [coordinates for coordinates , block in model.world.items() if block in [LIGHT_CLOUD , DARK_CLOUD]]
        assert len(cloud_blocks) >= sum(len(cloud) for cloud in clouds), "cloud blocks are not identified"