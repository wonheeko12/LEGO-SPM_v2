import legoeducation as le
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

# update these values to match the Connection Card
card_color = le.LEGO_COLOR_AZURE
card_serial = '4261'

# Connect to the Single Motor
singlemotor = le.SingleMotor()
singlemotor.connect(card_color=card_color, card_serial=card_serial)
# Connect to the Double Motor
doublemotor = le.DoubleMotor()
doublemotor.connect(card_color=card_color, card_serial=card_serial)
# Connect to the Color Sensor
colorsensor = le.ColorSensor()
colorsensor.connect(card_color=card_color, card_serial=card_serial)

# Check connection
if not (singlemotor.connected and doublemotor.connected and colorsensor.connected):
	print('Error connecting to hardware.')
	sys.exit(1) # error connecting

# Move single motor to find the z of surface at one point
def find_surface(degree_step, sensor_threshold):
	singlemotor.motor_set_speed(speed=10)

	probe_direction_up = le.MOTOR_MOVE_DIRECTION_COUNTERCLOCKWISE
	probe_direction_down = le.MOTOR_MOVE_DIRECTION_CLOCKWISE
	# direction clockwise or +deg: down, counterclockwise or -deg: up

	sensor_initial_reflection = colorsensor.sensor.reflection
	sensor_detected = abs(sensor_initial_reflection-colorsensor.sensor.reflection) < sensor_threshold
	# Print detected color for five seconds
	while(sensor_detected):
		print(f"LEGO Color reflection: {colorsensor.sensor.reflection}")
		singlemotor.motor_run_for_degrees(degrees=degree_step)
		# print(f'Current z position: {singlemotor.motor.position}')
		sensor_detected = abs(sensor_initial_reflection - colorsensor.sensor.reflection) < sensor_threshold
		time.sleep(0.01)
		# singlemotor.motor_stop()

	final_z = singlemotor.motor.position
	return final_z

# move z back to initial position
def return_to_initial_z(initial_z,tolerance):
	singlemotor.motor_set_speed(speed=20)
	probe_relative_height = singlemotor.motor.position
	while(abs(probe_relative_height-initial_z)>tolerance):
		singlemotor.motor_run_to_relative_position(position=initial_z)
		# print(f'Current z position: {singlemotor.motor.position}')
		probe_relative_height = singlemotor.motor.position
		time.sleep(0.01)

# move x or y back to initial position
def return_to_initial_xy(initial_xy, xydirection, tolerance):
	doublemotor.motor_set_speed(speed=20)
	probe_relative_height = doublemotor.motor[xydirection].position
	while(abs(probe_relative_height-initial_xy)>tolerance):
		doublemotor.motor_run_to_relative_position(motor=xydirection,position=initial_xy)
		# print(f'Current xy position: {doublemotor.motor[xydirection].position}')
		probe_relative_height = doublemotor.motor[xydirection].position
		time.sleep(0.01)

Npixel = 16
topographx = np.zeros((Npixel,Npixel))
topography = np.zeros((Npixel,Npixel))
topographz = np.zeros((Npixel,Npixel))

initial_xy = 0

sensor_threshold = 2
z_degree_step = 3
xy_degree_step = 10
initial_z = 0

singlemotor.motor_reset_relative_position()
doublemotor.motor_reset_relative_position()
doublemotor.motor_set_speed(speed=5)

# xydirection=le.MOTOR_RIGHT # MOTOR_RIGHT: x, MOTOR_LEFT: y

for i in range(Npixel):
	xydirection = le.MOTOR_RIGHT
	for j in range(Npixel):
		print(f'Current pixel : {i,j}')
		print(f'Current right position: {doublemotor.motor[le.MOTOR_RIGHT].position}')
		print(f'Current left position: {doublemotor.motor[le.MOTOR_LEFT].position}')
		surface_z = find_surface(z_degree_step, sensor_threshold)
		return_to_initial_z(initial_z,3)
		print(f'surface Z position: {surface_z}')
		topographx[i,j]=doublemotor.motor[le.MOTOR_RIGHT].position
		topography[i,j]=doublemotor.motor[le.MOTOR_LEFT].position
		topographz[i,j]=surface_z
		if j<Npixel-1:
			doublemotor.motor_run_for_degrees(motor=xydirection, direction=le.MOTOR_MOVE_DIRECTION_COUNTERCLOCKWISE, degrees=xy_degree_step)
		# time.sleep(0.1)
	return_to_initial_xy(initial_xy,xydirection,5)
	xydirection = le.MOTOR_LEFT
	if i<Npixel-1:
		doublemotor.motor_run_for_degrees(motor=xydirection, degrees=-xy_degree_step)

return_to_initial_xy(initial_xy,xydirection,5)

# surface_z = find_surface(degree_step, sensor_threshold)
# return_to_initial_z(initial_z)
# print(f'surface Z position: {surface_z}')

# plt.plot(topographx[0,:], -topographz[0,:])
# plt.plot(topography[0,:], -topographz[0,:])
plt.imshow(-topographz)
plt.show()

# Disconnect
singlemotor.disconnect()
doublemotor.disconnect()
colorsensor.disconnect()
sys.exit(0)  # successful execution
