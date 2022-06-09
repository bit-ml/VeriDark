# VeriDark Authorship Benchmark

The VeriDark benchmark contains several large-scale authorship verification and identification datasets, which should facilitate research into authorship analysis generally and enable building tools for the cybersecurity domain in particular.

Overview of the datasets:
1. [Datasets summary](#Summary)
2. [DarkReddit AV](#DarkReddit-authorship-verification-(AV)-dataset)
3. [DarkReddit+ AD](#DarkReddit+-authorship-verification-(AV)-large-dataset)
4. [DarkReddit+ AV](#DarkReddit+-authorship-verification-(AV)-large-dataset)
5. [DarkNet SilkRoad1 AV](#SilkRoad1-forum-dataset)
6. [DarkNet Agora AV](#Agora-forum-dataset)
## Summary
| dataset | train | val | test |
|---------|-------|-----|------|
|[MiniDarkReddit Authorship Verification](https://drive.google.com/file/d/1ok_CY59RhD0GgJqF1OOZMN592Zp9fgOY/view?usp=sharing) | 204 | 412 | 412 |
|[DarkReddit Authorship Identification](https://drive.google.com/file/d/1tVxMDVYzBSjg_iNTyrHzROwPs0uJmsDS/view?usp=sharing) | 6817 | 2275 | 2276 |
|[DarkReddit Authorship Verification](https://drive.google.com/file/d/1sPSJyN-WN_sBrmFSeKPSbxmKHT_r-twN/view?usp=sharing) | 106252 | 6124 | 6633 |
|[DarkNet SilkRoad1 Authorship Verification](https://drive.google.com/file/d/11mtP94YlYSB4dY2LoZW88Mavjger_vyd/view?usp=sharing) | 614656 | 34300 | 32255 |
|[DarkNet Agora Authorship Verification](https://drive.google.com/file/d/1ImO-xEVoxSyA21WPBS1Us14N1H7KVerV/view?usp=sharing) | 4195381 | 216570 | 219171 |

## DarkReddit Authorship Verification (AV) dataset 
This dataset was created by crawling comments from the `/r/darknet` subreddit.
The crawled data is saved to `original_darknet_comments.json`.
The dataset is small and was initially used to assess how well does training
on the PAN authorship verification datasets transfer to the smaller dataset.

## DarkReddit+ Authorship Verification (AV) large dataset
This dataset contains same author (SA) and different author (DA) pairs of comments
from the `/r/darknetmarkets` subreddit. Specifically, the comments were retrieved from 
the large Reddit comment [dataset](https://www.reddit.com/r/datasets/comments/3bxlg7/i_have_every_publicly_available_reddit_comment/) and saved to `darknet-dump.json`. We removed comments with less than 200 characters and stored them in `darknet-dump_filtered.json`. We split the authors into 3 disjoint sets of train authors, validation and test authors, making the authorship verification task an open setup. The SA and DA classes are balanced in all the

To create the AV dataset, call the `create_authorship_verification_darkreddit_dataset` function in the `read_darknet_vs_clear.py` file:
```
_ = create_authorship_verification_darkreddit_dataset(
    input_json_path=/darkweb2/darknet-dump_filtered.json,
    output_folder='/darkweb2'
)
```

|split | filename | size |  
|------|----------|------|
|train| ```darkreddit_authorship_verification_train_nodupe_anon.jsonl``` | 106252 |
|val| ```darkreddit_authorship_verification_val_nodupe_anon.jsonl``` | 6124 |
|test| ```darkreddit_authorship_verification_test_nodupe_anon.jsonl``` | 6633 |

## DarkReddit+ Authorship Identification (AD) dataset
This dataset is taken from the same Reddit comment dataset above. Specifically, we retrieved users who wrote in the `/r/darknet` subreddit as well as in other subreddits (`clearReddit`) and stored them in `darknet-dump-plus-clean.json`. We then removed comments with less than 200 characters and stored them in `darknet-dump-plus-clean_filtered.json`. After that, we removed users who had less than 5 comments in either `/r/darknet` or in `clearReddit`. Then we selected the top 10
most active users (most comments) in `/r/darknet`. The size of the total dataset is ~10k samples (train+validation+test splits). The task is a 10-way classification task in which, given a user comment, the model predicts the correct user.

To create the AD dataset, call the `create_authorship_attribution_darkreddit_dataset` function in the `read_darknet_vs_clear.py` file:
```
_ = create_authorship_attribution_darkreddit_dataset(
    input_json_path=/darkweb2/darknet-dump-plus-clean_filtered.json,
    output_folder='/darkweb2',
    K=10
)
```

## DarkNet Author Verification (AD) datasets
The two datasets are crawled from the [Agora](https://archive.org/download/dnmarchives/agora-forums.tar.xz) and [SilkRoad1](https://archive.org/download/dnmarchives/silkroad1-forums.tar.xz) forums from the
[Darknet market archives](https://www.gwern.net/DNM-archives).
The forums are then parsed with `parse.py` and saved as dictionaries to `/darkweb/author_comments_agora.json` and `/darkweb/author_comments_silkroad1.json`. Each author is mapped to a list of its comments.

To create the AV dataset for the Agora forum for example, call the `create_authorship_verification_darknet_dataset` function in the `read_darknet_vs_clear.py` file:
```
_ = create_authorship_verification_darknet_dataset(
    input_json_path='/darkweb/author_comments_agora_filtered.json',
    output_folder='/darkweb/darknet_authorship_verification/agora'
)
```
### SilkRoad1 forum dataset
Zip archive `darknet_authorship_verification_silkroad1_anon.zip`, containing the splits:
|split | filename | size |  
|------|----------|------|
|train| ```darknet_authorship_verification_train_nodupe_anon.jsonl``` | 614656 |
|val| ```darknet_authorship_verification_val_nodupe_anon.jsonl``` | 34300 |
|test| ```darknet_authorship_verification_test_nodupe_anon.jsonl``` | 32255 |
### Agora forum dataset
Zip archive `darknet_authorship_verification_agora_anon.zip`, containing the splits:
|split | filename | size |  
|------|----------|------|
|train| ```darknet_authorship_verification_train_nodupe_anon.jsonl``` | 4195381 |
|val| ```darknet_authorship_verification_val_nodupe_anon.jsonl``` | 216570 |
|test| ```darknet_authorship_verification_test_nodupe_anon.jsonl``` | 219171 |

