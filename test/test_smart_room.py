import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock
from unittest.mock import Mock

from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from src.smart_room import SmartRoom
from mock.senseair_s8 import SenseairS8


class TestSmartRoom(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_room_occupancy_should_return_true(self, mock_distance_sensor: Mock):
        mock_distance_sensor.return_value = True
        system = SmartRoom()
        occupied = system.check_room_occupancy()
        self.assertTrue(occupied)

    @patch.object(GPIO, "input")
    def test_check_enough_light(self, mock_light_sensor: Mock):
        mock_light_sensor.return_value = True
        system = SmartRoom()
        enough_light = system.check_enough_light()
        self.assertTrue(enough_light)

    @patch.object(SmartRoom, "check_room_occupancy")
    @patch.object(SmartRoom, "check_enough_light")
    @patch.object(GPIO, "output")
    def test_should_turn_on_light_when_person_is_in_room_and_not_enough_light(self, mock_light_bulb: Mock, mock_check_enough_light: Mock, mock_check_occupancy: Mock):
        mock_check_occupancy.return_value = True
        mock_check_enough_light.return_value = False
        system = SmartRoom()
        system.manage_light_level()
        mock_light_bulb.assert_called_with(system.LED_PIN, True)
