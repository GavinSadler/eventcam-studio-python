
from EventCamera import EventCamera

ec = EventCamera()

ec.connect()

print("Press enter to start loop")
input()

while True:
    print("External clock started")
    ec.startExternalClock()
    input()
    print("External clock stopped")
    ec.stopExternalClock()
    input()
