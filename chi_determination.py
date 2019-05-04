#open up the chi sweep detector spectrum
#allow the user to change the vmin and vmax of the images

#Allow the user to click on two different images and make them show up larger on the right hand side

#Allow the user to select the middle of the ones on the side

from h5 import h5grab_data

def return_chi_images_loc(file, detector_channel_loc = 'detector_channels/detector_scan/Main_Scan', zfill_num = 4):
    scan = h5grab_data(file, detector_channel_loc)
    scan_str = str(scan).zfill(zfill_num)
    im_loc = h5grab_data(file, 'images/{}'.format(scan_str))
    images_loc = ['images/{}/{}'.format(scan_str,
                                        loc) for loc in im_loc]
    return images_loc

def return_chi_images(file, images_loc):
    image_array = []
    for image in images_loc:
        image_array.append(h5grab_data(file,image))
    return image_array

