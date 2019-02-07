#
# Helper functions for reach task control

def init_spout(LED, touch, water):
    GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(touch, GPIO.IN)
    GPIO.setup(water, GPIO.OUT)
