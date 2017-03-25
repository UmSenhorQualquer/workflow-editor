import cv2, numpy as np; np.seterr(divide='ignore')
from polar import *
from scipy.ndimage import filters
from multiprocessing import Pool


def remove_vertical_objects( polar_grid, polar_border,
    ddepth = cv2.CV_16S, kernel_size = 1, scale= 1, delta = 0):
    """
    Remove all the vertical sets of pixels
    """
    grad_x = cv2.Scharr(polar_grid,ddepth,1,0,scale=scale, delta=delta,borderType = cv2.BORDER_REPLICATE)
    grad_y = cv2.Scharr(polar_grid,ddepth,0,1,scale=scale, delta=delta,borderType = cv2.BORDER_CONSTANT)
    grad_x = cv2.convertScaleAbs(grad_x); grad_x = cv2.bitwise_and(polar_border, grad_x)
    grad_y = cv2.convertScaleAbs(grad_y); grad_y = cv2.bitwise_and(polar_border, grad_y)
    mask = cv2.absdiff(grad_x, grad_y); 
    
    res = cv2.bitwise_and(grad_y, mask) 
    
    h,w = res.shape[:2]
    cv2.rectangle( res, (0,0),(w,(h//8)),   (0,0,0), -1 )
    cv2.rectangle( res, (0,h-(h//8)),(w,h), (0,0,0), -1 )
    return res

def f(parms):
    x,y,data, border, w = parms
    ddepth= cv2.CV_16S
    kernel_size= 1
    scale= 1
    delta= 0
    polar_grid, r, theta = reproject_image_into_polar(data, origin=(x, y))
    polar_border, r, theta = reproject_image_into_polar(border, origin=(x, y))
    clean_grad_y = remove_vertical_objects(polar_grid, polar_border, 
        ddepth = ddepth, kernel_size = kernel_size, scale= scale, delta = delta)
    cv2.rectangle( clean_grad_y, (0,0), (w,10), (0,0,0), -1 )
    return x,y, np.sum(clean_grad_y)




class FindCircle(object):



    def circle_center_estimation(self, image, p1=None, p2=None, size_factor=8, step=5,
        ddepth = cv2.CV_16S, kernel_size = 1, scale= 1, delta = 0, weights_map=None):
        """
        Estimate the circle center for the given image size factor and step.
        @type  step: integer
        @param step: Define the pixel jump between p1 and p2 box.
        """
        
        new_size = image.shape[1]//size_factor, image.shape[0]//size_factor
        min_size = min(new_size)
        if min_size<50: 
            if min_size==new_size[0]: size_factor = image.shape[1] // 50
            if min_size==new_size[1]: size_factor = image.shape[0] // 50
            new_size = image.shape[1]//size_factor, image.shape[0]//size_factor
        
        data = cv2.resize(image, new_size); h,w = data.shape[:2]
        if weights_map==None: weights_map = np.zeros_like(data, dtype=np.float32 )

        border = np.zeros_like( data, dtype=np.uint8 ); 
        cv2.rectangle( border, (4,4), (w-5,h-5), (255,255,255), -1 )

        if p1==None or p2==None: p1, p2 = (w//3, h//3), ( (w*2)//3, (h*2)//3 )
        
        params = []
        for x in range( p1[0], p2[0], step ):
            for y in range( p1[1], p2[1], step):
                params.append( (x,y,data,border,w) )

        pool = Pool(processes=8)
        result = pool.map(f, params)
        for x,y, val in result: weights_map[y, x] = val

        return weights_map, size_factor


    def find_circle_center(self, image):
        filters = [(10,3),(5,3),(4,2),(2,2),(1,1)]
        p1, p2, pos = None, None, None
        for scale, step in filters:
            if pos!=None:
                p1 = p1[0]//scale, p1[1]//scale
                p2 = p2[0]//scale, p2[1]//scale

            weights_map, size_factor = self.circle_center_estimation(image, p1, p2, size_factor=scale, step=step)    
            
            pos = np.unravel_index(weights_map.argmax(), weights_map.shape)
            pos = pos[1]*size_factor, pos[0]*size_factor

            p1 = pos[0]-step*size_factor+1, pos[1]-step*size_factor+1
            p2 = pos[0]+step*size_factor-1, pos[1]+step*size_factor-1

        return pos



    def fit_evaluator(self, img, y, blockSize):
        upper_line = img[y:y+blockSize,:]
        lower_line = img[y+blockSize:y+blockSize*2,:]
        return (np.sum(upper_line)/np.sum(lower_line))*np.nanvar(upper_line)
            

    def __find_radius(self, img, y_start=0, y_end=None, fase=0, blockSize=1):
        """
        Find the best fit in an image, for a 
        horizontal line having diferent colors intensity

        @type  img: numpy array
        @param img: One channel image.
        @type  y_start: start searching
        @param y_end: end searching.
        """
        #Check if the y_end is defined. If y_end is the height of the image
        if y_end==None: y_end = img.shape[0]-blockSize*2

        all_values = []
        for y in range(y_start, y_end, 1):
            all_values.append( [ self.fit_evaluator(img, y, blockSize), y] )

        all_values = sorted(all_values, key=lambda x: -x[0])
        _, y = all_values[0]

        return y


    def find_radius(self, image, center):
        polar_grid, coord_correspondence, theta = reproject_image_into_polar(image, origin=center)
        border = np.zeros_like( image, dtype=np.uint8 ); cv2.rectangle( border, (4,4), (border.shape[1]-5,border.shape[0]-5), (255,255,255), -1 )
        polar_border, coord_correspondence, theta = reproject_image_into_polar(border, origin=center)
        clean_grad_y = remove_vertical_objects(polar_grid, polar_border)
        polar_radius = self.__find_radius(clean_grad_y)
        
        cartasian_radius = int(round( coord_correspondence[polar_radius] ))

        #cv2.line(polar_grid, (0,y_r), (polar_grid.shape[1], y_r), (0,0,255), 1)
        #cv2.imshow("polar_grid", polar_grid);cv2.waitKey(0)
        return polar_radius, cartasian_radius
        
    def find_circle(self, image):
        pos = self.find_circle_center(image)
        polar_radius, cartasian_radius = self.find_radius(image, pos)

        return pos, cartasian_radius
        #cv2.circle(image, pos, y, (255,255,0), 4)
        #cv2.circle(image, pos, 3, (0,255,0), 4)
        #cv2.circle(image, (int(int(image.shape[1])//2),int(int(image.shape[0])//2)), 3, (255,0,0), 4)



if __name__ == "__main__":
    #capture = cv2.VideoCapture('/home/ricardo/Desktop/videos/marcia/virgin_wt_CS_3_2014-02-26-111742-0000.avi')
    #capture = cv2.VideoCapture('/home/ricardo/Desktop/videos/marcia/mated_wt_CS_1_2014-02-26-102445-0000.avi')
    capture = cv2.VideoCapture('/home/ricardo/Desktop/teste.avi')
    capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 400); res, image = capture.read()

    finder = FindCircle(image)
    center, radius = finder.find_circle(image)

    #cv2.line(polar_grid, (0,y_r), (polar_grid.shape[1], y_r), (255,0,255), 3)
    #cv2.imshow("ddd", polar_grid)

    cv2.circle(image, center, radius, (255,255,0), 4)
    cv2.circle(image, center, 3, (0,255,0), 4)
    cv2.circle(image, (int(int(image.shape[1])//2),int(int(image.shape[0])//2)), 3, (255,0,0), 4)

    #cv2.imshow("image", image)
    #cv2.waitKey(0)
