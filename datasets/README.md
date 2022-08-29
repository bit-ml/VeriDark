# VeriDark Authorship Datasets 

Overview:
1. [Datasets summary](#Summary)
2. [DarkReddit AV](#DarkReddit-authorship-verification-(AV)-dataset)
3. [DarkReddit+ AD](#DarkReddit+-authorship-verification-(AV)-large-dataset)
4. [DarkReddit+ AV](#DarkReddit+-authorship-verification-(AV)-large-dataset)
5. [DarkNet SilkRoad1 AV](#SilkRoad1-forum-dataset)
6. [DarkNet Agora AV](#Agora-forum-dataset)
## Summary

### Requesting the datasets
Due to ethical concerns regarding the potential misuse of our benchmark, we require the following additional information for granting permission to use our datasets:

1. The name of the person requesting access, together with their affiliations, job title and an e-mail address. If the person holds an institutional e-mail address, we strongly recommend using it instead of a personal e-mail address.

2. The intended usage for the dataset.

3. An acknowledgement that the dataset will be strictly used in an ethical manner. Non-ethical uses of the dataset include, but are not limited to:
	* using the datasets for the task of Language Modeling or similar generative algorithms.
	* building algorithms that could aid criminals to evade law enforcement organizations.
	* building algorithms that have the aim of unmasking undercover law enforcement agents.
	* building algorithms that could interfere with the activity of law enforcement agencies.
	* building algorithms that could lead to violating any article of the United Nations Universal Declaration of Human Rights.
	* building algorithms with the purpose of exposing the identity of reporters, individuals in the political realms, leakers, whistleblowers, dissidents, or other persons who are seeking to express an opinion about what they perceive is a particular injustice in the world, without regard to what that injustice may be.
	* building algorithms that can help entities discriminate, or exacerbate bias against other persons on the basis of race, color, religion, gender, gender expression, age, national origin, familiar status, ancestry, culture, disability, political views, sexual orientation, marital status, military status, social status, or who have other protected characteristics.
    
We strongly encourage the inclusion of an ethical statement and discussion in any work based on this dataset.
We do not encourage the distribution of the dataset in its current form to any other parties without our consent.

DISCLAIMER: Any personal information provided when requesting access to the dataset will be used just for deciding whether access to the dataset should be granted or not. We will not disclose your personal data.


| dataset | train | val | test | Google Drive link | Zenodo Link |
|---------|-------|-----|------|---------|--------|
|[MiniDarkReddit Authorship Verification](https://drive.google.com/file/d/1ok_CY59RhD0GgJqF1OOZMN592Zp9fgOY/view?usp=sharing) | 204 | 412 | 412 | [link](https://drive.google.com/file/d/1ok_CY59RhD0GgJqF1OOZMN592Zp9fgOY/view?usp=sharing) | - |
|[DarkReddit Authorship Identification](https://drive.google.com/file/d/1tVxMDVYzBSjg_iNTyrHzROwPs0uJmsDS/view?usp=sharing) | 6817 | 2275 | 2276 | [link](https://drive.google.com/file/d/1tVxMDVYzBSjg_iNTyrHzROwPs0uJmsDS/view?usp=sharing) | [link](https://zenodo.org/record/6998363) |
|[DarkReddit Authorship Verification](https://drive.google.com/file/d/1sPSJyN-WN_sBrmFSeKPSbxmKHT_r-twN/view?usp=sharing) | 106252 | 6124 | 6633 | [link](https://drive.google.com/file/d/1sPSJyN-WN_sBrmFSeKPSbxmKHT_r-twN/view?usp=sharing) | [link](https://zenodo.org/record/6998375) |
|[DarkNet SilkRoad1 Authorship Verification](https://drive.google.com/file/d/11mtP94YlYSB4dY2LoZW88Mavjger_vyd/view?usp=sharing) | 614656 | 34300 | 32255 | [link](https://drive.google.com/file/d/11mtP94YlYSB4dY2LoZW88Mavjger_vyd/view?usp=sharing) | [link](https://zenodo.org/record/6998371) |
|[DarkNet Agora Authorship Verification](https://drive.google.com/file/d/1ImO-xEVoxSyA21WPBS1Us14N1H7KVerV/view?usp=sharing) | 4195381 | 216570 | 219171 | [link](https://drive.google.com/file/d/1ImO-xEVoxSyA21WPBS1Us14N1H7KVerV/view?usp=sharing) | [link](https://zenodo.org/record/7018853) |

## DarkReddit Authorship Verification (AV) dataset 
This dataset was created by crawling comments from the `/r/darknet` subreddit.
The crawled data is saved to `original_darknet_comments.json`.
The dataset is small and was initially used to assess how well does training
on the PAN authorship verification datasets transfer to the smaller dataset.

## DarkReddit+ Authorship Verification (AV) large dataset
This dataset contains same author (SA) and different author (DA) pairs of comments
from the `/r/darknet` subreddit. Specifically, the comments were retrieved from 
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
|train| ```darkreddit_authorship_verification_train.json``` | 107042 |
|val| ```darkreddit_authorship_verification_val.json``` | 6164 |
|test| ```darkreddit_authorship_verification_test.json``` | 6680 |

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

## DarkNet Author Verification (AD) dataset
This dataset is crawled from the [Agora](https://archive.org/download/dnmarchives/agora-forums.tar.xz) and [SilkRoad1](https://archive.org/download/dnmarchives/silkroad1-forums.tar.xz) forums from the
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
Zip archive `darknet_authorship_verification_silkroad1.zip`, containing the splits:
|split | filename | size |  
|------|----------|------|
|train| ```darknet_authorship_verification_train.json``` | 713340 |
|val| ```darknet_authorship_verification_val.json``` | 39876 |
|test| ```darknet_authorship_verification_test.json``` | 37458 |
### Agora forum dataset
Zip archive `darknet_authorship_verification_agora.zip`, containing the splits:
|split | filename | size |  
|------|----------|------|
|train| ```darknet_authorship_verification_train.json``` | 5080890 |
|val| ```darknet_authorship_verification_val.json``` | 267528 |
|test| ```darknet_authorship_verification_test.json``` | 253644 |

