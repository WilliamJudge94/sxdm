function mda_import(loadmda_path,mda_path,detector_channel_limit,output_path)

%addpath '/home/will/Research/UIC/SXDM/Analysis';
%addpath '/home/will/Desktop/Processed_Data/SXDM_First_Cylce_NMC/Beam_Line_Data^/SXDM/APS_Filename^/2-Sample/MDA';

%Create output_file if it doesnt exist
if exist(output_path) == 2; 
else
    fid = fopen(output_path,'wt');
    fclose(fid);
end


addpath (loadmda_path);
%Create a loading bar for the user
bar = waitbar(1,'Program is Running, Please Wait');
counter = 1;

%collect all the mda files in the path
mda_files = dir(mda_path);
its_pre = size(mda_files);
its = its_pre(1);
filenames ={};

%Grab the list of all the mda files
for i = (3:its)
    full_name = horzcat(mda_path,'/',mda_files(i).name);
    filenames = [filenames, full_name];  
end

total_amount_pre = size(filenames);
total_amount = total_amount_pre(2);

%For each file open up all the channels and store values in hdf5
for filename = filenames
    mda_file = filename{1}(end-7:end-4);
    loading_str = ['Loading Scan - ' mda_file ' -  Please Wait' ];
    waitbar((counter-1)/total_amount,bar,loading_str);
    counter = counter + 1;
    %For each detector channel
    for detector_channel = (1:detector_channel_limit)
        %create a string of the detector challen for the h5 file
        detector_string = strcat('D',sprintf('%02d',detector_channel));
        %try to loadmda for that detector
        disp(detector_channel)
        try
            data=loadmda(filename{1},detector_channel,'n','n'); 
            clc
            close all
            data2=data(:,:,1);
            data2 = flipud(data2);
            data2 = transpose(data2);
            shape_data2  = size(data2);
            dim1 = shape_data2(1);
            dim2 = shape_data2(2);
        
        %if you can load it try to save the data to the appropriate
        %location in h5 file
            group = strcat('/mda/',mda_file,'/',detector_string);
            try
                h5create(output_path,group,[dim1 dim2]);  
            end
            try
                h5write(output_path,group,data2);
            end
        end
    end
end
close(bar)
clc
disp('Done')


        
