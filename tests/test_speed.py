import pyglet
import pytest
from unittest.mock import Mock
from tempus_fugit_minecraft.window import Window

@pytest.fixture(scope="class")
def window():
    yield Window()

class TestSpeed:
    @pytest.fixture(autouse=True)
    def teardown(self, window):
        window.walking_speed = 5

    def test_speed_up(self, window):
        assert window.walking_speed == 5

        window.speed_up()
        assert window.walking_speed == 10

        window.speed_up()
        assert window.walking_speed == 15

        for _ in range(0, 9):
            window.speed_up()
        assert window.walking_speed == 20  # 20 is the maximum speed

    def test_speed_down(self, window):
            window = Window()
            window.speed_up()
            
            assert window.walking_speed == 10

            window.speed_down() 
            assert window.walking_speed == 5      
            
            for _ in range(0,9):
                window.speed_down()

            assert window.walking_speed > 0 # Player will NOT stop walking

    def test_Q_key(self, window): # Test Q key down to increase speed
        assert window.walking_speed == 5

        window.on_key_press(pyglet.window.key.Q, Mock())
        assert window.walking_speed == 10

        window.on_key_press(pyglet.window.key.Q, Mock())
        assert window.walking_speed == 15

        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.Q, Mock())
        assert window.walking_speed == 20

    def test_E_key(self, window): # Test E key down to Decrease speed
        window.walking_speed = 20
        assert window.walking_speed == 20

        window.on_key_press(pyglet.window.key.E, Mock())
        assert window.walking_speed == 15

        window.on_key_press(pyglet.window.key.E, Mock())
        assert window.walking_speed == 10

        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.E, Mock())
        assert window.walking_speed == 5