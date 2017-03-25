#IMPORTS#

class OTPModuleGroup(#MODULES#):

    def __init__(self, **kwargs):
        super(OTPModuleGroup, self).__init__(**kwargs)

        #PARAMS#


if __name__ == "__main__":
    import cv2
    capture = cv2.VideoCapture("/home/ricardo/Desktop/30led.avi")

    module = OTPModuleGroup()

    while True:
        res, frame = capture.read()
        if not res: break;

        blobs = module.process(frame)
        for b in blobs: b.draw(frame)

        cv2.imshow("Capture", frame)

        key = cv2.waitKey(1)
        if key == ord('q'): break