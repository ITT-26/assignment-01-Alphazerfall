from DIPPID import SensorUDP
from vis import Visualizer

# use UPD (via WiFi) for communication
PORT = 5700
sensor = SensorUDP(PORT)
update_frequency = 10  # Hz

def main():
    visualizer = Visualizer(sensor=sensor, update_freq=update_frequency)   
    visualizer.run()

if __name__ == '__main__':
    main()