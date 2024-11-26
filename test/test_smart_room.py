import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock
from unittest.mock import Mock

from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from mock.senseair_s8 import SenseairS8
from src.smart_room import SmartRoom


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

    @patch.object(SmartRoom, "check_room_occupancy")
    @patch.object(SmartRoom, "check_enough_light")
    @patch.object(GPIO, "output")
    def test_should_not_turn_on_light_when_person_is_in_room_and_enough_light(self, mock_light_bulb: Mock, mock_check_enough_light: Mock, mock_check_occupancy: Mock):
        mock_check_occupancy.return_value = True
        mock_check_enough_light.return_value = True
        system = SmartRoom()
        system.manage_light_level()
        mock_light_bulb.assert_called_with(system.LED_PIN, False)

    @patch.object(Adafruit_BMP280_I2C,"temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_should_open_the_window(self, mock_servo: Mock, mock_temperature_sensors: Mock):
        mock_temperature_sensors.side_effect = [25, 28] # indoor, outdoor
        system = SmartRoom()
        system.manage_window()
        mock_servo.assert_called_with(12)

    @patch.object(Adafruit_BMP280_I2C,"temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_should_close_the_window(self, mock_servo: Mock, mock_temperature_sensors: Mock):
        mock_temperature_sensors.side_effect = [25, 22] # indoor, outdoor
        system = SmartRoom()
        system.manage_window()
        mock_servo.assert_called_with(2)

    @patch.object(Adafruit_BMP280_I2C,"temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_should_keep_the_window_closed_when_temperatures_outside_range(self, mock_servo: Mock, mock_temperature_sensors: Mock):
        mock_temperature_sensors.side_effect = [45, 48] # indoor, outdoor
        system = SmartRoom()
        system.manage_window()
        mock_servo.assert_called_with(2)

    @patch.object(SenseairS8,"co2")
    @patch.object(GPIO, "output")
    def test_should_turn_on_fan(self, mock_fan: Mock, mock_co2_sensor: Mock):
        mock_co2_sensor.return_value = 805
        system = SmartRoom()
        system.monitor_air_quality()
        mock_fan.assert_called_with(system.FAN_PIN, True)

    @patch.object(SenseairS8, "co2")
    @patch.object(GPIO, "output")
    def test_should_turn_off_fan(self, mock_fan: Mock, mock_co2_sensor: Mock):
        mock_co2_sensor.return_value = 400
        system = SmartRoom()
        system.monitor_air_quality()
        mock_fan.assert_called_with(system.FAN_PIN, False)
