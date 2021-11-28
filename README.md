# Unsupervised Unsupervised Sounding Object Localization with Bottom-Up and Top-Down Attention (USOL)

:herb: **[Unsupervised Unsupervised Sounding Object Localization with Bottom-Up and Top-Down Attention](https://vision.sjtu.edu.cn/files/wacv2022_USOL.pdf)**

Jiayin Shi, Chao Ma

*IEEE/CVF Winter Conference on Applications of Computer Vision (WACV), 2022.*

## Preparation

Besides data preparation introduced in our [baseline](https://github.com/ardasnck/learning_to_localize_sound_source), each sample folder should contain a list of region proposal rectangles as `.mat` extensions. 

## Training
```
python sound_localization_main.py \
--validation_on True  --validation_freq 1 --display_freq 1 --save_latest_freq 1 \
--val_dataset_file /path/to/test.txt \
--annotation_path /path_to_dataset/TestDataAnnotations \
--mode train --nThreads 8 --gpu_ids 1 \
--dataset_file /path/to/unsupervised_train_10k.txt \
--niter 10 --batchSize 30 --name name --optimizer adam --lr_rate 0.0001  --weight_decay 0.0
```

## Reference
We choose [Senocak et al.'s attention model](https://openaccess.thecvf.com/content_cvpr_2018/papers/Senocak_Learning_to_Localize_CVPR_2018_paper.pdf) as our baseline. The original code is listed as follows:
https://github.com/ardasnck/learning_to_localize_sound_source

Thanks for their wonderful work!