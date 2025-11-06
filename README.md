# [EMNLP 2025] The More, The Better? A Critical Study of Multimodal Context in Radiology Report Summarization
This repository contains data preprocessing code to reproduce the exclusive set as introduced in the paper.

# 1. Prepare labels from CheXpert labeler and TorchXrayVision 
- [TODO] Run [CheXpert labeler](https://github.com/stanfordmlgroup/chexpert-labeler) on [MIMIC-CXR (RRS)](https://github.com/jbdel/vilmedic/tree/main/data/make_datasets/mimic_cxr) dataset
- [TODO] Run [TorchXrayVision](https://github.com/mlmed/torchxrayvision) to obtain image labels for images in MIMIC-CXR
- Note that our chexpert labeler is modified to output `sentence_mapping.json` along with labels, which are sentences associated with each disease label

# 2. Build MIMIC-CXR-Exclusive set
- Run `mimic-exclusive.ipynb`, modify paths for required files accordingly
- The output will be findings with some critical sentences excluded (`train.findings.exclusive`) and reduced set of MIMIC-CXR-RRS (`train.findings.reduced`, `train.impression.reduced`, `train.image.reduced`), which are subset reduced to match the size of exclusive set

# Citation
If you find our work useful, please consider cite our paper:
```
@inproceedings{sim-etal-2025-better,
    title = "The More, The Better? A Critical Study of Multimodal Context in Radiology Report Summarization",
    author = "Sim, Mong Yuan  and
      Zhang, Wei Emma  and
      Dai, Xiang  and
      Fang, Biaoyan  and
      Ranjitkar, Sarbin  and
      Burlakoti, Arjun  and
      Taylor, Jamie  and
      Zhuang, Haojie",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2025",
    month = nov,
    year = "2025",
    address = "Suzhou, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.findings-emnlp.1040/",
    pages = "19116--19131",
    ISBN = "979-8-89176-335-7",
}
```

# Contact
If you have any questions or would like to have a discussion, please contact: mongyuansim [at] gmail [dot] com


