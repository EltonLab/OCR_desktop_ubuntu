class Arg():
    def __init__(self,project_path) -> None:
        self.alpha=1.0;
        self.beta=1.0;
        self.cls_batch_num=6
        self.cls_image_shape='3, 48, 192'; 
        self.cls_model_dir=f'{project_path}/model/ch_ppocr_mobile_v2.0_cls_infer';
        self.cls_thresh=0.9; 
        self.cpu_threads=10;
        self.crop_res_save_dir=f'{project_path}/output';
        self.det_db_box_thresh=0.6;
        self.det_db_score_mode='fast';
        self.det_db_thresh=0.3;
        self.det_db_unclip_ratio=1.5;
        self.det_east_cover_thresh=0.1;
        self.det_east_nms_thresh=0.2;
        self.det_east_score_thresh=0.8;
        self.det_limit_side_len=960;
        self.det_limit_type='max';
        self.det_model_dir=f'{project_path}/model/ch_PP-OCRv3_det_infer/'; #, detect text rect
        self.det_pse_box_thresh=0.85;    self.det_pse_min_area=16;
        self.det_pse_scale=1;   self.det_pse_thresh=0; 
        self.det_sast_nms_thresh=0.2; 
        self.det_sast_score_thresh=0.5; 
        self.e2e_algorithm='PGNet'; 
        self.e2e_char_dict_path=f'{project_path}/ppocr/utils/ic15_dict.txt';
        self.e2e_limit_side_len=768; 
        self.e2e_limit_type='max'; 
        self.e2e_model_dir=None; 
        self.e2e_pgnet_mode='fast';
        self.e2e_pgnet_score_thresh=0.5;
        self.e2e_pgnet_valid_set='totaltext'; 
        self.enable_mkldnn=False; 
        self.fourier_degree=5;
        self.gpu_id=0;     self.gpu_mem=500; 
        self.ir_optim=True;      self.label_list=['0', '180']; 
        self.max_batch_size=10;      self.max_text_length=25;
        self.min_subgraph_size=15;   self.page_num=0; 
        self.precision='fp32';  #fp32, fp16, int8     
        self.process_id=0; 
        self.rec_algorithm='SVTR_LCNet';     self.rec_batch_num=6; 
        self.rec_char_dict_path=f'{project_path}/ppocr/utils/en_dict.txt'; 
        self.rec_image_inverse=True;  self.rec_image_shape='3, 48, 320'; 
        self.rec_model_dir=f'{project_path}/model/en_PP-OCRv3_rec_infer/'; 
        self.return_word_box=False;  
        self.save_log_path=f'{project_path}/log_output/';  self.scales=[8, 16, 32];   
        self.show_log=True;    self.sr_batch_num=1;
        self.sr_image_shape='3, 32, 128';
        self.sr_model_dir=None;   self.total_process_num=1;
        self.use_dilation=False;
        self.use_gpu=True;   #todo
        self.use_mlu=False;  self.use_mp=False;    self.use_npu=False; 
        self.use_pdserving=False; 
        self.use_space_char=True;
        self.use_tensorrt=False;      self.use_xpu=False;
        self.warmup=False