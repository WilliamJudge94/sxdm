import os

# multi.py
def better_multi(self, rows, columns, med_blur_distance=4,
                 med_blur_height=10, stdev_min=35, nprocs=1):

    """DEPRECIATED

    :param self:
    :param rows:
    :param columns:
    :param med_blur_distance:
    :param med_blur_height:
    :param stdev_min:
    :param nprocs:
    :return:
    """

    def worker(its, out_q):
        major_out = []
        for chunk in its:
            self, row, column, image_array, median_blur_distance, median_blur_height, stdev_min = chunk
            out = pixel_analysis(self, row, column, image_array, median_blur_distance, median_blur_height, stdev_min)
            major_out.append(out)
        out_q.put(major_out)

    self.median_blur_distance = med_blur_distance
    self.median_blur_height = med_blur_height
    self.stdev_min = stdev_min
    background_dic_basic = scan_background(self, multiplier = 0)
    image_array = centering_det(self, group='filenumber')
    self.image_array = np.asarray(image_array)
    its = iterations(self, rows, columns)
    chunksize = int(math.ceil(len(its) / float(nprocs)))

    out_q = Queue()
    procs = []

    for i in tqdm(range(nprocs), desc="Procs"):
        chunk_its = its[chunksize * i:chunksize * (i + 1)]
        p = Process(
            target=worker, args=(chunk_its, out_q))
        procs.append(p)
        p.start()

    resultdict = []
    for i in tqdm(range(nprocs), desc="Results"):
        resultdict.append(out_q.get())

    for pr in tqdm(procs, desc="Join"):
        pr.join()

    master_results = []
    for re in resultdict:
        master_results.extend(re)

    return master_results


# pixel.py
def pixel_analysis(self, row, column, image_array,
                   median_blur_distance, median_blur_height, stdev_min):
    """Depreciated for centroid_pixel_analysis
    :param self:
    :param row:
    :param column:
    :param image_array:
    :param median_blur_distance:
    :param median_blur_height:
    :param stdev_min:
    :return:
    """
    if column == 0:
        if ram_check() > 90:
            return False

    pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
    destination = h5get_image_destination(self=self, pixel=pix)
    each_scan_diffraction = sum_pixel(self=self, images_loc=destination)

    # Background Correction
    backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    summed_dif = np.sum(each_scan_diffraction_post, axis=0)

    # pooled: Work In Progress
    # q_theta = Queue()
    # q_chi = Queue()

    # ttheta_pool_results = Process(target = theta_maths, args =
    # (summed_dif, median_blur_distance, median_blur_height,stdev_min,q_theta))
    # chi_pool_results = Process(target = chi_maths, args =
    # (summed_dif, median_blur_distance, median_blur_height,stdev_min,q_chi))

    # ttheta_pool_results.start()
    # chi_pool_results.start()

    # ttheta_pool_results.join()
    # chi_pool_results.join()

    # ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = q_theta.get()
    # chi, chi_centroid, chi_centroid_finder = q_chi.get()

    # seperate analysis (SLOW)

    ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = theta_maths(summed_dif,
                                                                           median_blur_distance,
                                                                           median_blur_height, stdev_min)
    chi, chi_centroid, chi_centroid_finder = chi_maths(summed_dif,
                                                       median_blur_distance,
                                                       median_blur_height, stdev_min)

    full_roi = np.sum(ttheta2)

    return (row, column), summed_dif, ttheta, chi,\
           ttheta_centroid_finder, ttheta_centroid, chi_centroid_finder, chi_centroid, full_roi


# postprocess.py
def make_video(image_folder, output_folder=False, outimg=None, fps=23, size=None,
               is_color=True, format="XVID"):
    """DEPRECIATED
    Create a video from a list of images.
    @param      outvid      output video
    @param      images      list of images to use in the video
    @param      fps         frame per second
    @param      size        size of each frame
    @param      is_color    color
    @param      format      see http://www.fourcc.org/codecs.php
    @return                 see http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
    The function relies on http://opencv-python-tutroals.readthedocs.org/en/latest/.
    By default, the video will have the size of the first image.
    It will resize every image to this size before adding them to the video.
    """

    if output_folder == False:
        output_folder = '/home/will/Desktop/video.mp4'
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images = sorted(images)

    from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
    fourcc = VideoWriter_fourcc(*format)
    vid = None
    for image in images:
        image = image_folder + '/' + image
        if not os.path.exists(image):
            raise FileNotFoundError(image)
        img = imread(image)
        if vid == None:
            if size == None:
                size = img.shape[1], img.shape[0]
            vid = VideoWriter(output_folder, fourcc, float(fps), size, is_color)
        if size[0] != img.shape[1] and size[1] != img.shape[0]:
            img = resize(img, size)
        vid.write(img)
    vid.release()
    return vid

#multi.py
def analysis(self, rows, columns, default_cores=True,
             stdev_min=35, med_blur_distance=4,
             med_blur_height=10, multiplier=1):
    """Runs the pixel_analysis function defined in pixel.py through starmap multiprocessing

    Paramters
    =========

    self

    rows

    columns

    default_cores

    stdev_min

    med_blur_distance

    med_blur_height

    multiplier

    Return
    ======
    A multi-dimesional array consisting of:
    row_column - row and column values 'for the current index'
    summed_dif - summed diffraction ' '
    ttheta - a 1D 2theta array  ' '
    chi - a 1D chi array ' '
    ttheta_corr - a 1D 2theta array that has been median blurred ' '
    ttheta_centroid - a multi-dimensional array consisting of 2theta centroid values ' '
    chi_cor -  - a 1D chi array that has been median blurred ' '
    chi_centroid - a multi-dimensional array consisting of chi centroid values ' '
    full_roi - a corrected region of interest on the current selection
    """

    # Add background correction to analysis

    self.median_blur_distance = med_blur_distance
    self.median_blur_height = med_blur_height
    self.stdev_min = stdev_min
    background_dic_basic = scan_background(self, multiplier=multiplier)

    if default_cores == True:
        core_count = int(cpu_count()/2)
    else:
        core_count = default_cores
    image_array = centering_det(self, group='filenumber')
    self.image_array = np.asarray(image_array)
    its = iterations(self, rows, columns)
    pool = Pool(core_count)

    # Run multiprocessing on pixel iterations
    results = parallel_progbar(pixel_analysis, its, nprocs=default_cores, starmap=True)

    pool.close()
    pool.join()

    if False in results:
        warnings.warn('Not Enough RAM For Batch Processing. Program Auto Quit. Please Use Slower Functionality')
    self.results = results
    print('Results Saved As self.results')