# VeriDark Authorship Analysis Datasets 

### Requesting the datasets
Due to ethical concerns regarding the potential misuse of our benchmark, we require additional information for granting permission to use our datasets, which you can submit in the Zenodo request access forms (see Zenodo links below). We request the following information:

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


| dataset | train | val | test | task | Link |
|---------|-------|-----|------|---------|--------|
|[MiniDarkReddit](https://drive.google.com/file/d/1ok_CY59RhD0GgJqF1OOZMN592Zp9fgOY/view?usp=sharing) | 204 | 412 | 412 | Authorship Verification | [Google Drive link](https://drive.google.com/file/d/1ok_CY59RhD0GgJqF1OOZMN592Zp9fgOY/view?usp=sharing) |
|DarkReddit+ | 6817 | 2275 | 2276 | Authorship Identification | [Zenodo link](https://zenodo.org/record/6998363) |
|DarkReddit+ | 106252 | 6124 | 6633 | Authorship Verification | [Zenodo link](https://zenodo.org/record/6998375) |
|SilkRoad1 | 614656 | 34300 | 32255 | Authorship Verification| [Zenodo link](https://zenodo.org/record/6998371) |
|Agora | 4195381 | 216570 | 219171 | Authorship Verification | [Zenodo link](https://zenodo.org/record/7018853) |

## DarkReddit dataset for Authorship Verification (AV)
This dataset was created by crawling comments from the `/r/darknet` subreddit. The dataset is small and was introduces in this [paper](https://arxiv.org/abs/2112.05125) to assess how well does training on the PAN authorship verification datasets transfer to the smaller dataset.

## DarkReddit+ dataset for Authorship Verification (AV)
This dataset contains same author (SA) and different author (DA) pairs of comments
from the defunct `/r/darknetmarkets` subreddit. Specifically, the comments were retrieved from 
the large Reddit comment [dataset](https://www.reddit.com/r/datasets/comments/3bxlg7/i_have_every_publicly_available_reddit_comment/). We removed comments with less than 200 characters.  We split the authors into 3 disjoint sets of train authors, validation and test authors, making the authorship verification task an open setup. The SA and DA classes are balanced in all the splits.

## DarkReddit+ dataset for Authorship Identification (AI)
This dataset is taken from the same Reddit comment dataset above. Specifically, we retrieved users who wrote in the `/r/darknetmarkets` subreddit as well as in other subreddits (`clearReddit`). We then removed comments with less than 200 characters. After that, we removed users who had less than 5 comments in either `/r/darknetmarkets` or in `clearReddit`. Then we selected the top 10 most active users (most comments) in `/r/darknetmarkets`. The size of the total dataset is ~10k samples (train+validation+test splits). The task is a 10-way classification task in which, given a user comment, the model predicts the correct user.


## Agora dataset for Authorship Verification (AV)
The Agora dataset was collected from the [Agora](https://archive.org/download/dnmarchives/agora-forums.tar.xz) marketplace forum data, which was obtained from the [Darknet market archives](https://www.gwern.net/DNM-archives).


## SilkRoad1 dataset for Authorship Verification (AV)
The SilkRoad1 dataset was collected from the [SilkRoad1](https://archive.org/download/dnmarchives/silkroad1-forums.tar.xz) marketplace forum data, which was obtained from the [Darknet market archives](https://www.gwern.net/DNM-archives).
