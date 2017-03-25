import sys; sys.path.insert( 0, '.' )
import cv2
from numpy import *
from matplotlib.backends.backend_agg import FigureCanvasAgg
import math
from PyQt4 import QtGui
import os
import OpenGL.GL  as GL

### Function to calculate the background #######################################
def CalculateBackground( capture, nFrames, updateFunction=None ):

    n_total_frames =    int(    capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT) )
    n_frames_step =     int(    round( n_total_frames/nFrames  ) )

    width = int(round(capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH ) ))
    height = int(round(capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT) ))
    backgroundSum = zeros( (height,width), dtype=float64  )

    step = 100.0/float(nFrames)
    count = 0

    for i in range(1, n_total_frames, n_frames_step):

        if updateFunction: updateFunction(count)

        capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, i)
        (success, frame) = capture.read()

        if success:
            frame = cv2.resize(frame, (width,height))
            frame = cv2.cvtColor( frame , cv2.cv.CV_RGB2GRAY )
            backgroundSum += frame
        count += step

    capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
    return array( backgroundSum/nFrames ,  dtype=uint8)
################################################################################


def pointsDistance(p1, p2):
    return  math.hypot(p2[0]-p1[0], p2[1]-p1[1])


def rotateImage(shape, image, angle):
    image_center = ( int(round(shape[2]/2)), int(round(shape[3]/2)))
    rot_mat = cv2.getRotationMatrix2D(image_center,angle,1.0)
    result = cv2.warpAffine(image, rot_mat, (shape[2], shape[3]),flags=cv2.INTER_LINEAR)
    return result


def fig2data (fig ):
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    w,h = canvas.get_width_height()
    s = canvas.tostring_rgb()
    x = fromstring(s, uint8)
    x.shape = h, w, 3
    return x

def rgb2qimage(rgb):
        """Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
        have three dimensions with the vertical, horizontal and RGB image axes."""
        if len(rgb.shape) != 3:
            raise ValueError("rgb2QImage can expects the first (or last) dimension to contain exactly three (R,G,B) channels")
        if rgb.shape[2] != 3:
            raise ValueError("rgb2QImage can only convert 3D arrays")

        h, w, channels = rgb.shape

        # Qt expects 32bit BGRA data for color images:
        bgra = empty((h, w, 4), uint8, 'C')
        bgra[...,0] = rgb[...,2]
        bgra[...,1] = rgb[...,1]
        bgra[...,2] = rgb[...,0]
        bgra[...,3].fill(255)

        result = QtGui.QImage(bgra.data, w, h, QtGui.QImage.Format_RGB32)
        result.ndarray = bgra
        return result

def createRectanglePoints( start, end ):
    return [ start, (end[0],start[1]), end, (start[0],end[1]) ]

def createEllipsePoints( start, end ):
    width = end[0]-start[0]
    height = end[1]-start[1]
    center = ( start[0] + width/2, start[1] + height/2 )
    
    distance = pointsDistance(start, end )
    nPoints = distance / 30
    if nPoints<8:nPoints = 8.0

    points = []
    for angleR in arange(0, math.pi*2, math.pi/nPoints):
        x = int(round(center[0] + width/2 * cos(angleR) ))
        y = int(round(center[1] + height/2 * sin(angleR)))
        points.append( ( x,y) )
    return points

def createCirclePoints( center, radius):
    nPoints = radius / 30
    if nPoints<8:nPoints = 8.0

    points = []
    for angleR in arange(0, math.pi*2, math.pi/nPoints):
        x = int(round(center[0] + radius * cos(angleR) ))
        y = int(round(center[1] + radius * sin(angleR)))
        points.append( ( x,y) )
    return points


def getFileInSameDirectory(file, name):
    #module_path = os.path.abspath(os.path.dirname(file))
    module_path = os.path.dirname(file)
    return os.path.join(module_path, name)

    filename = os.path.join(module_path, name)
    dirs = filename.split("main.exe\\")
    dest_filename = dirs[1].replace("./", "").replace("/", "_").replace(".\\", "").replace("\\", "_")[-20:]
    return dirs[1]

def str_split(s, seps):
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    return res

def point_inside_polygon(x,y,poly):
    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside


def drawGLCircle(radius):

    GL.glBegin(GL.GL_POLYGON)
    for angle in arange(0, math.pi*2.0, .2):
        x1 = math.sin(-angle+math.pi)*0.5;
        y1 = math.cos(angle+math.pi)*0.5;
        x2 = math.sin(angle)*radius;
        y2 = math.cos(angle)*radius;
        GL.glTexCoord2f(x1+0.5, y1+0.5)
        GL.glVertex3f(x2,y2,0.0);
    GL.glEnd()


def drawGLCube(r):

    GL.glBegin(GL.GL_QUADS);

    z = 0
    
    # Front Face
    GL.glNormal3f( 0.0, 0.0, 1.0)                 # Normal Pointing Towards Viewer
    GL.glTexCoord2f(0.0, 1.0)
    GL.glVertex3f(-r, -r,  z) # Point 1 (Front)
    GL.glTexCoord2f(1.0, 1.0)
    GL.glVertex3f( r, -r,  z) # Point 2 (Front)
    GL.glTexCoord2f(1.0, 0.0)
    GL.glVertex3f( r,  r,  z) # Point 3 (Front)
    GL.glTexCoord2f(0.0, 0.0)
    GL.glVertex3f(-r,  r,  z) # Point 4 (Front)
    """# Back Face
    GL.glNormal3f( 0.0, 0.0,-1.0)                 # Normal Pointing Away From Viewer
    GL.glTexCoord2f(1.0, 1.0)
    GL.glVertex3f(-r, -r, -z) # Point 1 (Back)
    GL.glTexCoord2f(1.0, 0.0)
    GL.glVertex3f(-r,  r, -z) # Point 2 (Back)
    GL.glTexCoord2f(0.0, 0.0)
    GL.glVertex3f( r,  r, -z) # Point 3 (Back)
    GL.glTexCoord2f(0.0, 1.0)
    GL.glVertex3f( r, -r, -z) # Point 4 (Back)
    # Top Face
    GL.glNormal3f( 0.0, 1.0, 0.0)                 # Normal Pointing Up
    GL.glTexCoord2f(0.0, 0.0)
    GL.glVertex3f(-r,  r, -z) # Point 1 (Top)
    GL.glTexCoord2f(0.0, 1.0)
    GL.glVertex3f(-r,  r,  z) # Point 2 (Top)
    GL.glTexCoord2f(1.0, 1.0)
    GL.glVertex3f( r,  r,  z) # Point 3 (Top)
    GL.glTexCoord2f(1.0, 0.0)
    GL.glVertex3f( r,  r, -z) # Point 4 (Top)
    # Bottom Face
    GL.glNormal3f( 0.0,-1.0, 0.0)                 # Normal Pointing Down
    GL.glTexCoord2f(1.0, 0.0)
    GL.glVertex3f(-r, -r, -z) # Point 1 (Bottom)
    GL.glTexCoord2f(0.0, 0.0)
    GL.glVertex3f( r, -r, -z) # Point 2 (Bottom)
    GL.glTexCoord2f(0.0, 1.0)
    GL.glVertex3f( r, -r,  z) # Point 3 (Bottom)
    GL.glTexCoord2f(1.0, 1.0)
    GL.glVertex3f(-r, -r,  z) # Point 4 (Bottom)
    # Right face
    GL.glNormal3f( 1.0, 0.0, 0.0)                 # Normal Pointing Right
    GL.glTexCoord2f(1.0, 1.0)
    GL.glVertex3f( r, -r, -z) # Point 1 (Right)
    GL.glTexCoord2f(1.0, 0.0)
    GL.glVertex3f( r,  r, -z) # Point 2 (Right)
    GL.glTexCoord2f(0.0, 0.0)
    GL.glVertex3f( r,  r,  z) # Point 3 (Right)
    GL.glTexCoord2f(0.0, 1.0)
    GL.glVertex3f( r, -r,  z) # Point 4 (Right)
    # Left Face
    GL.glNormal3f(-1.0, 0.0, 0.0)                 # Normal Pointing Left
    GL.glTexCoord2f(0.0, 1.0)
    GL.glVertex3f(-r, -r, -z) # Point 1 (Left)
    GL.glTexCoord2f(1.0, 1.0)
    GL.glVertex3f(-r, -r,  z) # Point 2 (Left)
    GL.glTexCoord2f(1.0, 0.0)
    GL.glVertex3f(-r,  r,  z) # Point 3 (Left)
    GL.glTexCoord2f(0.0, 0.0)
    GL.glVertex3f(-r,  r, -z) # Point 4 (Left)
    """
    GL.glEnd()

    
def LoadOpenGLTexture(textFile):
    img = cv2.imread(textFile)
    GL.glEnable(GL.GL_TEXTURE_2D)
    texture =  GL.glGenTextures(1)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, len(img[0]), len(img), 0, GL.GL_BGR, GL.GL_UNSIGNED_BYTE, img)
    return texture

def clock():
    return cv2.getTickCount() / cv2.getTickFrequency()


#####################################################################################
################# Used for calculate 2 points intersection ##########################
#####################################################################################

def perp( a ) :
    b = empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# return 
def seg_intersect(a1,a2, b1,b2) :
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = dot( dap, db)
    num = dot( dap, dp )
    if denom==0: return None
    intersection = (num / denom)*db + b1
    x_min_a, x_max_a, y_min_a, y_max_a = min(a1[0],a2[0]),max(a1[0],a2[0]),min(a1[1],a2[1]),max(a1[1],a2[1])
    x_min_b, x_max_b, y_min_b, y_max_b = min(b1[0],b2[0]),max(b1[0],b2[0]),min(b1[1],b2[1]),max(b1[1],b2[1])
    """if  (x_min_a<=intersection[0]<=x_max_a and y_max_a<=intersection[1]<=y_max_a) and \
        (x_min_b<=intersection[0]<=x_min_b and y_min_b<=intersection[1]<=y_max_b):
        return intersection
    else:
        return None
    """
    return intersection

def seg_intersect2(a1,a2, b1,b2) :
    x = float32(a1 - b1)
    d1 = float32(a2 - a1)
    d2 = float32(b2 - b1)

    cross = d1[0]*d2[1] - d1[1]*d2[0]    
    if (abs(cross) ==0): return None
    t1 = -(x[0] * d2[1] - x[1] * d2[0])/cross
    intersection = a1 + d1 * t1
    #print "----", intersection, a1, d1, t1

    x_min_a, x_max_a, y_min_a, y_max_a = min(a1[0],a2[0]),max(a1[0],a2[0]),min(a1[1],a2[1]),max(a1[1],a2[1])
    x_min_b, x_max_b, y_min_b, y_max_b = min(b1[0],b2[0]),max(b1[0],b2[0]),min(b1[1],b2[1]),max(b1[1],b2[1])
    if  (x_min_a<=intersection[0]<=x_max_a and y_min_a<=intersection[1]<=y_max_a) and \
        (x_min_b<=intersection[0]<=x_max_b and y_min_b<=intersection[1]<=y_max_b):
        return int32(intersection)
    else:
        return None

def find_seg_intersect(a1, a2, b1, b2):
    v1 = a2[0]-a1[0], a2[1]-a1[1]
    v2 = b2[0]-b1[0], b2[1]-b1[1]
    k_b = (a1[1] + (b1[0]*v1[1])/v1[0] - (a1[0]*v1[1])/v1[0] - v2[1]) * (v2[1]- (v2[0]*v1[1])/v1[0])
    print k_b
    if 0<=k_b<=1: return b1[0]+k_b*v2[0], b1[1]+k_b*v2[1]
    else: return None

def merge_contours( contour1, contour2 , image):
    new_contour = []

    p1, p2 = None, None
    for i in range(0, len(contour1) ):
        a1, a2 = contour1[i-1][0], contour1[i][0]

        for j in range(0, len(contour2) ):    
            b1, b2 = contour2[j-1][0], contour2[j][0]

            img = image.copy()

            intersection = find_seg_intersect(a1, a2, b1, b2)
            if intersection!=None:
                new_contour.append( [intersection] )

                cv2.circle( img, tuple(intersection), 1, (50), 3 )
                
                if p1==None: p1 = (i-1, j+1)
                elif p2==None:  p2 = (i-1, j-1)

                if p1!=None and p2!=None:
                    #print p1, p2
                    for c in range(p1[1], p2[1]+1):
                        p = contour2[c][0]
                        #new_contour.append([p])
                    p1, p2 = None, None
                #else:
                #    if p1==None: new_contour.append([a2])
                #break
            
            cv2.circle( img, tuple(a1), 1, (200), 3 )
            cv2.circle( img, tuple(a2), 1, (200), 3 )
            cv2.circle( img, tuple(b1), 1, (200), 3 )
            cv2.circle( img, tuple(b2), 1, (200), 3 )

            cv2.imshow("image", img)
            key = cv2.waitKey(0)
            if key == ord('q'): exit()
            
        #if p1==None: new_contour.append([a2])
        #else: print p1, p2
        #print a1,a2

    return int32(new_contour)


        



class RingBuffer:
    def __init__(self, size):
        self._size = size
        self.data = []

    def append(self, x):
        if self._size==len(self.data): self.data.pop(0)
        self.data.append(x)

    def get(self, index=None): 
        if index!=None:
            return self.data[index]
        else:
            return self.data

    def set(self, index, obj): self.data[index] = obj

    def count(self): 
        return len(self.data)

    def printValues(self):
        for x in self.data:
            print x, " | ", 
        print ""



def biggestContour(contours):
    biggest = None
    biggerArea = 0
    for blob in contours:
        area = cv2.contourArea(blob)
        if area>biggerArea:
            biggerArea = area
            biggest = blob
    return biggest








if __name__ == "__main__":

    #ellipse = createEllipsePoints(( 10, 10), (100, 100))
    ellipse = createRectanglePoints(( 10, 20), (100, 120))
    cnt1 = int32(map(lambda x:[x], ellipse) ) 

    #ellipse = createEllipsePoints(( 50, 10), (150, 100))
    ellipse = createRectanglePoints(( 150, 10), (250, 100))
    cnt2 = int32(map(lambda x:[x], ellipse) ) 

    image = ones( (300, 300), dtype=uint8 )
    
    cnt1 = concatenate((cnt1, cnt2), axis=0)
    cnt1 = cv2.convexHull(cnt1)

    cv2.polylines(image, [cnt1], True, (100)) 
    #cv2.polylines(image, [cnt2], True, (100)) 

    merged = merge_contours(cnt1, cnt2, image)
    print merged
    cv2.polylines(image, [merged], False, (255), 3) 
    

    cv2.imshow("image", image)
    key = cv2.waitKey(0)
    if key == ord('q'): exit()


