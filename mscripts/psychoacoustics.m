function psychoacoustics(File, FileName, LoudnessPath, SharpnessPath)
    
    result_l = struct();
    result_s = struct();
    
    file = readmatrix(File);

    x = file(2:end ,1);

    total_points = length(x);
    num_of_segments = floor(total_points/25000);

    for seg = 1:num_of_segments
        starting_point = (seg-1) * 25000 + 1;
        ending_point = (seg) * 25000; 

        each_sample = x(starting_point:ending_point);
        
        [Loudness, SpecLoudness] = acousticLoudness(each_sample, 48000, 'TimeVarying', true);
        result_l(seg).time_varying_loudness = Loudness;

        TvSharpness = acousticSharpness(each_sample, 48000, 'TimeVarying', true);
        result_s(seg).time_varying_sharpness = TvSharpness;

    end

    T = struct2table(result_l);
    loudness_file_name = [LoudnessPath filesep FileName '_loudness.csv'];
    writetable(T, loudness_file_name);

    T = struct2table(result_s);
    sharpness_file_name = [SharpnessPath filesep FileName '_sharpness.csv'];
    writetable(T, sharpness_file_name);

end