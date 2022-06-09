import json
import os
import re
import uuid
from sklearn.model_selection import train_test_split
from typing import Callable
from itertools import accumulate
from numpy import histogram
from numpy.random import choice
import random
from tqdm import tqdm

def create_example(label, a1, a2, d1, d2):
    return {
        'id': str(uuid.uuid1()),
        'same': label,
        'authors': [a1, a2],
        'pair': [d1, d2]
    }

def remove_small_comments_darkreddit_and_clean(data):
    """
    Removes small comments (<200 characters) from the reddit dump,
    which contains authors with comments in both darkreddit as well
    as other subreddits.
    Arguments:
        data: dictionary read from darknet-dump-plus-clean.json
    """
    new_data = {}

    for author, author_data in data.items():
        dark_comments = [e['message'] for e in author_data['darknet'] if len(e['message']) > 200]
        clear_comments = [e['message'] for e in author_data['clear'] if len(e['message']) > 200]
        if len(dark_comments) > 0 and len(clear_comments) > 0:
            new_data[author] = {}
            new_data[author]['darknet'] = dark_comments
            new_data[author]['clear'] = clear_comments
    
    return new_data

def remove_small_comments_darkreddit(data):
    """
    Removes small comments (<200 characters) from the reddit dump,
    which contains authors with comments in both darkreddit as well
    as other subreddits.
    Arguments:
        data: dictionary read from darknet-dump.json
    """
    new_data = {}

    for author, author_data in data.items():
        comments = [e['message'] for e in author_data if len(e['message']) > 200]
        if len(comments) > 0:
            new_data[author] = comments
    
    return new_data

def remove_small_comments_darknet(data):
    """
    Removes small comments (<200 characters) from the DarkNet
    raw files, which contains authors with comments from a certain
    forum (Agora, SilkRoad etc.)
    Arguments:
        data: dictionary with darknet author comments data
        (e.g. author_comments_agora.json)
    """
    new_data = {}
    MAX_LEN = 21000
    for author, author_data in data.items():
        comments = [e[:MAX_LEN] for e in author_data if len(e) > 200]

        if len(comments) > 0:
            new_data[author] = comments
    
    return new_data

def pipeline_remove_small_comments(
        input_json_path: str, 
        removal_fn: Callable,
        output_json_path:str ):
    # read darkreddit/darknet data
    data = json.load(open(input_json_path))
    print("#authors before: ", len(data))

    # modify data
    new_data = removal_fn(data)

    print("#authors after: ", len(new_data))
    # dump new_data
    with open(output_json_path, 'w') as fp:
        json.dump(
            new_data,
            fp, 
            indent=2
        )

def get_stats(path_to_json: str):
    examples = json.load(open(path_to_json))
    comments_length = [len(e['comment']) for e in examples]
    avg_comment_length = sum(comments_length)/len(comments_length)
    print("Dataset: ", path_to_json)
    print("\tdataset size: ", len(comments_length))
    print("\tavg comment length: %d characters" % (avg_comment_length))
    print("\tmax comment length: %d characters" % (max(comments_length)))

def get_stats_darkreddit(data):
    """
        data: dictionary of darknet-dump_filtered.json
    """
    print("#authors = ", len(data))
    comment_lengths = {}
    for a, author_data in data.items():
        comment_lengths[a] = [len(e) for e in author_data]
        #print(a, ': ', len(comment_lengths[a]), ' comments')

    avg_comment_lengths = [sum(e)/len(e) for e in comment_lengths.values()]
    min_comment_lengths = [min(e) for e in comment_lengths.values()]
    max_comment_lengths = [max(e) for e in comment_lengths.values()]
    num_comments = [len(comments) for comments in data.values()]
    avg_number_of_comments = sum(num_comments)/len(data)
    min_number_of_comments = min(num_comments)
    max_number_of_comments = max(num_comments)
    #print(num_comments)
    print("Average #comments per user = ", avg_number_of_comments)
    print("Min #comments per user = ", min_number_of_comments)
    print("Max #comments per user = ", max_number_of_comments)
    print("Average comment length per user = ", sum(avg_comment_lengths) / len(avg_comment_lengths))
    print("Average min length comment per user = ", sum(min_comment_lengths) / len(min_comment_lengths))
    print("Average max length comment per user = ", sum(max_comment_lengths) / len(max_comment_lengths))
    print("Minimum global length: ", min(min_comment_lengths))
    print("Maximum global length: ", max(max_comment_lengths))

    l = sorted(comment_lengths.items(), key=lambda x: len(x[1]), reverse=True)
    for e in l[:100]:
        print(e[0], ': ', len(e[1]), ' comments')

    hist, edges = histogram(avg_comment_lengths, 'auto')
    print(hist)
    print(edges)

def get_av_dataset_stats(input_json: str):
        """
            input_json: path to AV dataset
        """
        with open(input_json) as fp:
            data = json.load(fp)
            sa_lengths, da_lengths = [], []
            sa_length_diffs, da_length_diffs = [], []
            sa_count, da_count = 0, 0
            for ex in data:
                if ex['same']:
                    sa_count += 1
                    c1, c2 = ex['pair'][0], ex['pair'][1]
                    sa_lengths += [len(c1), len(c2)]
                    sa_length_diffs.append(abs(len(c1) - len(c2)))
                else:
                    da_count += 1
                    c1, c2 = ex['pair'][0], ex['pair'][1]
                    da_lengths += [len(c1), len(c2)]
                    da_length_diffs.append(abs(len(c1) - len(c2)))
        
        print("Dataset: ", input_json)
        print("\t#SA = %d, DA = %d" % (sa_count, da_count))
        print("\tSA pairs")
        print("\t\tavg length (characters): ", sum(sa_lengths) / len(sa_lengths))
        print("\t\tavg length difference between comments: ", sum(sa_length_diffs)/len(sa_length_diffs))
        print("\tDA pairs")
        print("\t\tavg length (characters): ", sum(da_lengths) / len(da_lengths))
        print("\t\tavg length difference between comments: ", sum(da_length_diffs)/len(da_length_diffs))


def create_authorship_attribution_darkreddit_dataset(
        input_json_path: str, 
        output_folder: str,
        K: int):
    """
    Creates a K-way classification dataset from the DarkReddit dump.
    Specifically, the most K active users in 'darknet' (who also have
    written in other clear subreddits) represent K distinct classes.
    The train/val/test splits are going to be saved in the `output_folder`.

    Arguments:
        input_json_path: path to the DarkReddit dump containing authors
        and their comments in the 'darknet' subreddit, as well as in
        'clearnet' (other subreddits)
        output_folder: where to save the train/val/test splits
        K: how many classes (authors) to consider
    """
    data = json.load(
        open(input_json_path)
    )

    # sort authors by most comments
    print("Counting #comments")
    num_dark_comments, num_clear_comments = {}, {}
    for a, a_data in data.items():
        num_dark_comments[a] = len(a_data['darknet'])
        num_clear_comments[a] = len(a_data['clear'])

    # sanity check
    dark_authors = set(num_dark_comments.keys())
    clear_authors = set(num_clear_comments.keys())
    print("Total authors = %d, #dark_authors = %d, #clear_authors = %d" % (
        len(data), len(dark_authors), len(clear_authors)
    ))

    # drop authors who have less than 5 comments in either
    # clear or darkreddit
    infrequent_authors = [a for a in num_dark_comments.keys() if num_dark_comments[a] < 5
        or num_clear_comments[a] < 5
    ]
    print("#infrequent authors = %d (out of %d)" % (len(infrequent_authors), len(num_dark_comments)))

    # remove infrequent authors
    for a in infrequent_authors:
        del data[a]
        del num_clear_comments[a]
        del num_dark_comments[a]

    print("After removing infrequent authors")
    dark_authors = set(num_dark_comments.keys())
    clear_authors = set(num_clear_comments.keys())
    print("Total authors = %d, #dark_authors = %d, #clear_authors = %d" % (
        len(data), len(dark_authors), len(clear_authors)
    ))

    most_commented_dark_authors = sorted(
        num_dark_comments.items(),
        key=lambda x: x[1],
        reverse=True
    )

    print("top 30 authors with most comments in darkreddit")
    for e in most_commented_dark_authors[:30]:
        #print(e)
        author, num_comments = e[0], e[1]
        print('author=%s, #dark = %s, #clear = %d' % (
            author, num_comments, num_clear_comments[author]
        ))
    
    # select top K authors
    # create training/validation/test set
    labels = [e[0] for e in most_commented_dark_authors[:K]]

    print("Creating dataset")
    train_examples, val_examples, test_examples = [], [], []
    for author in labels:
        dark_comments = data[author]['darknet']
        num_dark_comments = len(dark_comments)

        train_comments, test_comments = train_test_split(
            dark_comments, test_size=0.2, random_state=1
        )

        train_comments, val_comments = train_test_split(
            train_comments, test_size=0.25, random_state=1
        )

        def create_example(a, c):
            return {
                "author": a,
                "comment": c
            }
        
        print("author %s: #train = %d, #val = %d, #test = %d" % (
            author, len(train_comments), len(val_comments), len(test_comments)
        ))
        train_examples += [create_example(author, c) for c in train_comments]
        val_examples += [create_example(author, c) for c in val_comments]
        test_examples += [create_example(author, c) for c in test_comments]

    train_path = os.path.join(output_folder, "darkreddit_authorship_attribution_train.json")
    val_path = os.path.join(output_folder, "darkreddit_authorship_attribution_val.json")
    test_path = os.path.join(output_folder, "darkreddit_authorship_attribution_test.json")

    # json.dump(train_examples, open(train_path, "w"), indent=2)
    # json.dump(val_examples, open(val_path, "w"), indent=2)
    # json.dump(test_examples, open(test_path, "w"), indent=2)
    
    return train_examples, val_examples, test_examples


def create_authorship_verification_darknet_dataset(
    input_json_path: str,
    output_folder: str
):
    """
    Path to json file containing author comments from the DarkNet 
    forums (e.g. for SilkRoad -> `author_comments_silkroad1.json`)
    """
    with open(input_json_path) as fp:
        print("reading data")
        data = json.load(fp)

    all_authors = list(data.keys())
    single_comment_authors = [a for a in all_authors if len(data[a]) == 1]
    multi_comment_authors = [a for a in all_authors if len(data[a]) > 1]
    print("Number of authors: ", len(all_authors))
    print("Single comment authors: ", len(single_comment_authors))
    print("Multiple comment authors: ", len(multi_comment_authors))
    num_test_authors = int(0.05*len(all_authors))
    test_authors = random.sample(all_authors, num_test_authors)
    other_authors = set(all_authors).difference(set(test_authors))
    val_authors = random.sample(list(other_authors), num_test_authors)
    train_authors = list(other_authors.difference(set(val_authors)))   
    print("Train authors")
    print("\tsingle comment train authors: ", len([a for a in train_authors if len(data[a]) == 1]))
    print("\tmulti comment train authors: ", len([a for a in train_authors if len(data[a]) > 1]))

    print("Val authors")
    print("\tsingle comment val authors: ", len([a for a in val_authors if len(data[a]) == 1]))
    print("\tmulti comment val authors: ", len([a for a in val_authors if len(data[a]) > 1]))

    print("Test authors")
    print("\tsingle comment test authors: ", len([a for a in test_authors if len(data[a]) == 1]))
    print("\tmulti comment test authors: ", len([a for a in test_authors if len(data[a]) > 1]))

    train_examples, val_examples, test_examples = [], [], []
    # create SA test pairs
    print("creating SA test pairs")
    for author in test_authors:
        comments = data[author].copy()
        random.shuffle(comments)
        while len(comments) >= 2:
            c1 = comments.pop()
            c2 = comments.pop()
            test_examples.append(create_example(True, author, author, c1, c2))
    
    print("creating DA test pairs")
    # create DA test pairs
    def create_probs(authors, cumulative: bool=False):
        """
        Create probabilities to weight samples differently
        """
        probs = [2 if len(data[a]) == 1 else 1 for a in authors]
        if cumulative:
            cum_probs = list(accumulate(probs))
            probs = [e/cum_probs[-1] for e in cum_probs]
        else:
            sum_probs = sum(probs)
            probs = [e/sum_probs for e in probs]

        return probs

    test_size = len(test_examples)
    test_probs = create_probs(test_authors)
    test_authors_single_comment = [a for a in test_authors if len(data[a]) == 1]
    test_authors_multi_comment = [a for a in test_authors if len(data[a]) > 1]
    while test_size > 0:
        # favor single-comment authors more than multiple-comments
        # authors, as the latter appeared in same-author pairs 
        # as well
        # p = random.random()
        # if p < 0.67:
        #     a1, a2 = random.sample(test_authors_single_comment, k=2)
        #     c1, c2 = data[a1][0], data[a2][0]
        # else:
        #     a1 = random.sample(test_authors_single_comment, k=1)[0]
        #     a2 = random.sample(test_authors_multi_comment, k=1)[0]
        #     c1 = data[a1][0]
        #     c2 = random.choice(data[a2])
        a1, a2 = random.sample(test_authors, k=2)
        c1, c2 = random.choice(data[a1]), random.choice(data[a2])
        test_examples.append(create_example(False, a1, a2, c1, c2))
        test_size -= 1

    print("creating SA val pairs")
    for author in val_authors:
        comments = data[author].copy()
        random.shuffle(comments)
        while len(comments) >= 2:
            c1 = comments.pop()
            c2 = comments.pop()
            val_examples.append(create_example(
                True, author, author, c1, c2
            ))

    print("creating DA val pairs")
    # create DA val pairs
    val_size = len(val_examples)
    #val_probs = create_probs(val_authors)
    val_authors_single_comment = [a for a in val_authors if len(data[a]) == 1]
    val_authors_multi_comment = [a for a in val_authors if len(data[a]) > 1]
    while val_size > 0:
        # p = random.random()
        # if p < 0.67:
        #     a1, a2 = random.sample(val_authors_single_comment, k=2)
        #     c1, c2 = data[a1][0], data[a2][0]
        # else:
        #     a1 = random.sample(val_authors_single_comment, k=1)[0]
        #     a2 = random.sample(val_authors_multi_comment, k=1)[0]
        #     c1 = data[a1][0]
        #     c2 = random.choice(data[a2])
        a1, a2 = random.sample(val_authors, k=2)
        c1, c2 = random.choice(data[a1]), random.choice(data[a2])
        val_examples.append(create_example(False, a1, a2, c1, c2))
        val_size -= 1    

    print("creating SA train pairs")
    for author in train_authors:
        comments = data[author].copy()
        random.shuffle(comments)
        while len(comments) >= 2:
            c1 = comments.pop()
            c2 = comments.pop()
            train_examples.append(create_example(
                True, author, author, c1, c2
            ))

    print("creating DA train pairs")
    # create DA train pairs
    train_size = len(train_examples)
    train_authors_single_comment = [a for a in train_authors if len(data[a]) == 1]
    train_authors_multi_comment = [a for a in train_authors if len(data[a]) > 1]
    while train_size > 0:
        # p = random.random()
        # if p < 0.67:
        #     a1, a2 = random.sample(train_authors_single_comment, k=2)
        #     c1, c2 = data[a1][0], data[a2][0]
        # else:
        #     a1 = random.sample(train_authors_single_comment, k=1)[0]
        #     a2 = random.sample(train_authors_multi_comment, k=1)[0]
        #     c1 = data[a1][0]
        #     c2 = random.choice(data[a2])
        a1, a2 = random.sample(train_authors, k=2)
        c1, c2 = random.choice(data[a1]), random.choice(data[a2])
        train_examples.append(create_example(False, a1, a2, c1, c2))
        train_size -= 1
        if train_size % 10000 == 0:
            print("train size left: ", train_size)

    print("train examples: ", len(train_examples))
    print("val examples: ", len(val_examples))
    print("test examples: ", len(test_examples))

    if not os.path.exists(output_folder):
        print(output_folder, " folder does not exist, trying to create it")
        os.makedirs(output_folder)
    
    if len(os.listdir(output_folder)) > 0:
        print(output_folder, " is not empty, abort")
    else:
        train_path = os.path.join(output_folder, "darknet_authorship_verification_train.json")
        val_path = os.path.join(output_folder, "darknet_authorship_verification_val.json")
        test_path = os.path.join(output_folder, "darknet_authorship_verification_test.json")

        json.dump(train_examples, open(train_path, "w"), indent=2)
        json.dump(val_examples, open(val_path, "w"), indent=2)
        json.dump(test_examples, open(test_path, "w"), indent=2)

    return train_examples, val_examples, test_examples

def create_authorship_verification_darkreddit_dataset(
    input_json_path: str,
    output_folder: str
):
    """
    Path to DarkReddit only (no clearReddit), filtered dump 
    (darknet-dump_filtered.json file).
    """
    with open(input_json_path) as fp:
        print("reading data")
        data = json.load(fp)

    del data['[deleted]']
    del data['AutoModerator']

    # create open set AV dataset (test/val authors are not seen during train)
    all_authors = list(data.keys())
    num_test_authors = int(0.05*len(all_authors))
    test_authors = random.sample(all_authors, num_test_authors)
    other_authors = set(all_authors).difference(set(test_authors))
    val_authors = random.sample(list(other_authors), num_test_authors)
    train_authors = list(other_authors.difference(set(val_authors)))

    print("#authors: ", len(all_authors))
    print("#authors train: ", len(train_authors))
    print("#authors val: ", len(val_authors))
    print("#authors test: ", len(test_authors))

    train_examples, val_examples, test_examples = [], [], []
    # create SA test pairs
    print("creating SA test pairs")
    for author in test_authors:
        comments = data[author].copy()
        random.shuffle(comments)
        while len(comments) >= 2:
            c1 = comments.pop()
            c2 = comments.pop()
            test_examples.append(create_example(True, author, author, c1, c2))
    
    print("creating DA test pairs")
    # create DA test pairs
    test_size = len(test_examples)
    while test_size > 0:
        a1, a2 = random.sample(test_authors, k=2)
        a1_comments, a2_comments = data[a1], data[a2]
        c1 = random.choice(a1_comments)
        c2 = random.choice(a2_comments)
        test_examples.append(create_example(False, a1, a2, c1, c2))
        test_size -= 1

    print("creating SA val pairs")
    for author in val_authors:
        comments = data[author].copy()
        random.shuffle(comments)
        while len(comments) >= 2:
            c1 = comments.pop()
            c2 = comments.pop()
            val_examples.append(create_example(
                True, author, author, c1, c2
            ))

    print("creating DA val pairs")
    # create DA val pairs
    val_size = len(val_examples)
    while val_size > 0:
        a1, a2 = random.sample(val_authors, k=2)
        a1_comments, a2_comments = data[a1], data[a2]
        c1 = random.choice(a1_comments)
        c2 = random.choice(a2_comments)
        val_examples.append(create_example(False, a1, a2, c1, c2))
        val_size -= 1

    print("creating SA train pairs")
    for author in train_authors:
        comments = data[author].copy()
        random.shuffle(comments)
        while len(comments) >= 2:
            c1 = comments.pop()
            c2 = comments.pop()
            train_examples.append(create_example(
                True, author, author, c1, c2
            ))

    print("creating DA train pairs")
    # create DA train pairs
    train_size = len(train_examples)
    while train_size > 0:
        a1, a2 = random.sample(train_authors, k=2)
        a1_comments, a2_comments = data[a1], data[a2]
        c1 = random.choice(a1_comments)
        c2 = random.choice(a2_comments)
        train_examples.append(create_example(False, a1, a2, c1, c2))
        train_size -= 1

    print("train examples: ", len(train_examples))
    print("val examples: ", len(val_examples))
    print("test examples: ", len(test_examples))

    if not os.path.exists(output_folder):
        print(output_folder, " folder does not exist, trying to create it")
        os.makedirs(output_folder)
    
    if len(os.listdir(output_folder)) > 0:
        print(output_folder, " is not empty, abort")
    else:
        train_path = os.path.join(output_folder, "darkreddit_authorship_verification_train.json")
        val_path = os.path.join(output_folder, "darkreddit_authorship_verification_val.json")
        test_path = os.path.join(output_folder, "darkreddit_authorship_verification_test.json")

        json.dump(train_examples, open(train_path, "w"), indent=2)
        json.dump(val_examples, open(val_path, "w"), indent=2)
        json.dump(test_examples, open(test_path, "w"), indent=2)

    return train_examples, val_examples, test_examples

def anonymize_authors_aa(train_jsonl_path: str, val_jsonl_path: str, 
            test_jsonl_path: str):
    """
    Replaces train/val/test usernames with 'user1', 'user2', ..., 'userN'. 
    for the authorship attribution dataset.
    Writes the modified files into .jsonl files

    Arguments:
        train_jsonl_path: path to .json train file 
            (i.e. '/darkweb2/darkreddit_authorship_attribution_train.jsonl')
        val_jsonl_path: path to .json val file 
        test_jsonl_path: path to .json test file 
    """
    train_jsonl_anon_path = train_jsonl_path.replace('.json', '_anon.jsonl')
    val_jsonl_anon_path = val_jsonl_path.replace('.json', '_anon.jsonl')
    test_jsonl_anon_path = test_jsonl_path.replace('.json', '_anon.jsonl')
    usernames_dict = {}
    user_index = 1
    train_lengths, val_lengths, test_lengths = [], [], []
    with open(train_jsonl_path, 'r') as in_fp, open(train_jsonl_anon_path, 'w') as out_fp:
        examples = json.load(in_fp)
        for example in examples:
            a = example['author']
            c = example['comment']

            if a in usernames_dict:
                a_anon = usernames_dict[a]
            else:
                a_anon = f'user{user_index}'
                usernames_dict[a] = a_anon
                user_index += 1

            example['author'] = a_anon
            json.dump(example, out_fp)
            out_fp.write('\n')

            tokens_c = len(re.split("\s+", c.strip(), flags=re.UNICODE))
            train_lengths.append(tokens_c)
    
    train_size = len(train_lengths)
    num_train_authors = user_index - 1
    train_stats = {
        'size': train_size,
        'num_authors': num_train_authors,
        'avg_comment_length': sum(train_lengths) / len(train_lengths),
        'comment_lengths': train_lengths
    }        

    with open(val_jsonl_path, 'r') as in_fp, open(val_jsonl_anon_path, 'w') as out_fp:
        examples = json.load(in_fp)
        for example in examples:
            a = example['author']
            c = example['comment']

            if a in usernames_dict:
                a_anon = usernames_dict[a]
            else:
                a_anon = f'user{user_index}'
                usernames_dict[a] = a_anon
                user_index += 1

            example['author'] = a_anon
            json.dump(example, out_fp)
            out_fp.write('\n')
            tokens_c = len(re.split("\s+", c.strip(), flags=re.UNICODE))
            val_lengths.append(tokens_c)

    val_size = len(val_lengths)
    num_val_authors = user_index - 1
    val_stats = {
        'size': val_size,
        'num_authors': num_val_authors,
        'avg_comment_length': sum(val_lengths) / len(val_lengths),
        'comment_lengths': val_lengths
    }

    with open(test_jsonl_path, 'r') as in_fp, open(test_jsonl_anon_path, 'w') as out_fp:
        examples = json.load(in_fp)
        for example in examples:
            a = example['author']
            c = example['comment']

            if a in usernames_dict:
                a_anon = usernames_dict[a]
            else:
                a_anon = f'user{user_index}'
                usernames_dict[a] = a_anon
                user_index += 1

            example['author'] = a_anon
            json.dump(example, out_fp)
            out_fp.write('\n')
            tokens_c = len(re.split("\s+", c.strip(), flags=re.UNICODE))
            test_lengths.append(tokens_c)
            
    test_size = len(test_lengths)
    num_test_authors = user_index - 1
    test_stats = {
        'size': test_size,
        'num_authors': num_test_authors,
        'avg_comment_length': sum(test_lengths) / len(test_lengths),
        'comment_lengths': test_lengths
    }

    return train_stats, val_stats, test_stats

def anonymize_authors(train_jsonl_path: str, val_jsonl_path: str, 
            test_jsonl_path: str):
    """
    Replaces train/val/test usernames with 'user1', 'user2', ..., 'userN'. 
    for the authorship verification datasets

    Arguments:
        train_jsonl_path: path to .jsonl train file 
            (i.e. '/darkweb/darkreddit_authorship_verification_val.jsonl')
        val_jsonl_path: path to .jsonl val file 
        test_jsonl_path: path to .jsonl test file 
    """
    train_jsonl_anon_path = train_jsonl_path.replace('.jsonl', '_anon.jsonl')
    val_jsonl_anon_path = val_jsonl_path.replace('.jsonl', '_anon.jsonl')
    test_jsonl_anon_path = test_jsonl_path.replace('.jsonl', '_anon.jsonl')

    usernames_dict = {}
    user_index = 1
    train_lengths, val_lengths, test_lengths = [], [], []
    same_examples, diff_examples = 0, 0
    with open(train_jsonl_path, 'r') as in_fp, open(train_jsonl_anon_path, 'w') as out_fp:
        for line in tqdm(in_fp):
            line_dict = json.loads(line)
            #print(line_dict)
            a1, a2 = line_dict['authors']
            if a1 in usernames_dict:
                a1_anon = usernames_dict[a1]
            else:
                a1_anon = f'user{user_index}'
                usernames_dict[a1] = a1_anon
                user_index += 1

            if a2 in usernames_dict:
                a2_anon = usernames_dict[a2]
            else:
                a2_anon = f'user{user_index}'
                usernames_dict[a2] = a2_anon
                user_index += 1

            #modify entry
            line_dict['authors'] = [a1_anon, a2_anon]

            if line_dict['same']:
                same_examples += 1
            else:
                diff_examples += 1

            #write entry in anonymized .jsonl file
            json.dump(line_dict, out_fp)
            out_fp.write('\n')

            # count words
            c1, c2 = line_dict['pair'][0], line_dict['pair'][1]
            tokens_c1 = len(re.split("\s+", c1.strip(), flags=re.UNICODE))
            tokens_c2 = len(re.split("\s+", c2.strip(), flags=re.UNICODE))
            train_lengths += [tokens_c1, tokens_c2]
    
    train_size = len(train_lengths) // 2
    num_train_authors = user_index - 1
    train_stats = {
        'size': train_size,
        'same_author_examples': same_examples,
        'different_author_examples': diff_examples,
        'num_authors': num_train_authors,
        'avg_comment_length': sum(train_lengths) / len(train_lengths),
        'comment_lengths': train_lengths
    }

    # anonymize validation set
    same_examples, diff_examples = 0, 0
    with open(val_jsonl_path, 'r') as in_fp, open(val_jsonl_anon_path, 'w') as out_fp:
        for line in tqdm(in_fp):
            line_dict = json.loads(line)
            #print(line_dict)
            a1, a2 = line_dict['authors']
            if a1 in usernames_dict:
                a1_anon = usernames_dict[a1]
            else:
                a1_anon = f'user{user_index}'
                usernames_dict[a1] = a1_anon
                user_index += 1

            if a2 in usernames_dict:
                a2_anon = usernames_dict[a2]
            else:
                a2_anon = f'user{user_index}'
                usernames_dict[a2] = a2_anon
                user_index += 1

            #modify entry
            line_dict['authors'] = [a1_anon, a2_anon]

            if line_dict['same']:
                same_examples += 1
            else:
                diff_examples += 1

            #write entry in anonymized .jsonl file
            json.dump(line_dict, out_fp)
            out_fp.write('\n')

            # count words
            c1, c2 = line_dict['pair'][0], line_dict['pair'][1]
            tokens_c1 = len(re.split("\s+", c1.strip(), flags=re.UNICODE))
            tokens_c2 = len(re.split("\s+", c2.strip(), flags=re.UNICODE))
            val_lengths += [tokens_c1, tokens_c2]

    val_size = len(val_lengths) // 2
    num_val_authors = user_index - 1 - num_train_authors
    val_stats = {
        'size': val_size,
        'same_author_examples': same_examples,
        'different_author_examples': diff_examples,
        'num_authors': num_val_authors,
        'avg_comment_length': sum(val_lengths) / len(val_lengths),
        'comment_lengths': val_lengths
    }

    # anonymize test set
    same_examples, diff_examples = 0, 0
    with open(test_jsonl_path, 'r') as in_fp, open(test_jsonl_anon_path, 'w') as out_fp:
        for line in tqdm(in_fp):
            line_dict = json.loads(line)
            #print(line_dict)
            a1, a2 = line_dict['authors']
            if a1 in usernames_dict:
                a1_anon = usernames_dict[a1]
            else:
                a1_anon = f'user{user_index}'
                usernames_dict[a1] = a1_anon
                user_index += 1

            if a2 in usernames_dict:
                a2_anon = usernames_dict[a2]
            else:
                a2_anon = f'user{user_index}'
                usernames_dict[a2] = a2_anon
                user_index += 1

            #modify entry
            line_dict['authors'] = [a1_anon, a2_anon]

            if line_dict['same']:
                same_examples += 1
            else:
                diff_examples += 1

            #write entry in anonymized .jsonl file
            json.dump(line_dict, out_fp)
            out_fp.write('\n')

            # count words
            c1, c2 = line_dict['pair'][0], line_dict['pair'][1]
            tokens_c1 = len(re.split("\s+", c1.strip(), flags=re.UNICODE))
            tokens_c2 = len(re.split("\s+", c2.strip(), flags=re.UNICODE))
            test_lengths += [tokens_c1, tokens_c2]

    test_size = len(test_lengths) // 2
    num_test_authors = user_index - 1 - num_train_authors - num_val_authors
    test_stats = {
        'size': test_size,
        'same_author_examples': same_examples,
        'different_author_examples': diff_examples,
        'num_authors': num_test_authors,
        'avg_comment_length': sum(test_lengths) / len(test_lengths),
        'comment_lengths': test_lengths
    }

    return train_stats, val_stats, test_stats


if __name__ == '__main__':
    reddit_darknet_path = '/darkweb2/darknet-dump.json'
    reddit_filtered_darknet_path = '/darkweb2/darknet-dump_filtered.json'
    reddit_darknet_plus_clean_path = '/darkweb2/darknet-dump-plus-clean.json'
    reddit_filtered_darknet_plus_clean_path = '/darkweb2/darknet-dump-plus-clean_filtered.json'

    darknet_agora_path = '/darkweb/author_comments_agora.json'
    darknet_filtered_agora_path = '/darkweb/author_comments_agora_filtered.json'
    darknet_silkroad1_path = '/darkweb/author_comments_silkroad1.json'
    darknet_filtered_silkroad1_path = '/darkweb/author_comments_silkroad1_filtered.json'

    PATHS = {
        'agora': {
            'train': '/darkweb/darknet_authorship_verification/agora/darknet_authorship_verification_train_nodupe.jsonl',
            'val': '/darkweb/darknet_authorship_verification/agora/darknet_authorship_verification_val_nodupe.jsonl',
            'test': '/darkweb/darknet_authorship_verification/agora/darknet_authorship_verification_test_nodupe.jsonl'
        },
        'silkroad1': {
            'train': '/darkweb/darknet_authorship_verification/silkroad1/darknet_authorship_verification_train_nodupe.jsonl',
            'val': '/darkweb/darknet_authorship_verification/silkroad1/darknet_authorship_verification_val_nodupe.jsonl',
            'test': '/darkweb/darknet_authorship_verification/silkroad1/darknet_authorship_verification_test_nodupe.jsonl'
        },
        'darkreddit': {
            'train': '/darkweb2/darkreddit_authorship_verification/darkreddit_authorship_verification_train_nodupe.jsonl',
            'val': '/darkweb2/darkreddit_authorship_verification/darkreddit_authorship_verification_val_nodupe.jsonl',
            'test': '/darkweb2/darkreddit_authorship_verification/darkreddit_authorship_verification_test_nodupe.jsonl'
        },
        'darkreddit_aa': {
            'train': '/darkweb2/darkreddit_authorship_attribution/darkreddit_authorship_attribution_train.json',
            'val': '/darkweb2/darkreddit_authorship_attribution/darkreddit_authorship_attribution_val.json',
            'test': '/darkweb2/darkreddit_authorship_attribution/darkreddit_authorship_attribution_test.json'
        }
    }

    # pipeline_remove_small_comments(
    #     input_json_path=darknet_agora_path,
    #     removal_fn=remove_small_comments_darknet,
    #     output_json_path=darknet_filtered_agora_path
    # )

    # with open(filtered_darknet_path) as fp:
    #     data = json.load(fp)
  
    # get_stats_darkreddit(data)

    # this cell is used to create the K-way author classification 
    # data = json.load(
    #     open(filtered_darknet_plus_clean_path)
    # )

    # create AA dataset
    # _ = create_authorship_attribution_darkreddit_dataset(
    #     input_json_path=filtered_darknet_plus_clean_path,
    #     output_folder='/darkweb2',
    #     K=10
    # )
    
    # create AV dataset from DarkReddit
    # create_authorship_verification_darkreddit_dataset(
    #     input_json_path=filtered_darknet_path,
    #     output_folder='/darkweb2'
    # )

    # create AV dataset from DarkWeb (SilkRoad1)
    # create_authorship_verification_darknet_dataset(
    #     input_json_path=darknet_filtered_agora_path,
    #     output_folder="/darkweb/darknet_authorship_verification/agora"
    # )

    # anonymize AV dataset
    # dataset = 'agora'
    # train_stats, val_stats, test_stats = anonymize_authors(
    #     PATHS[dataset]['train'], 
    #     PATHS[dataset]['val'], 
    #     PATHS[dataset]['test']
    # )
    # json.dump(
    #     [train_stats, val_stats, test_stats],
    #     open(os.path.join(os.path.dirname(PATHS[dataset]['train']), 'dataset_stats.json'), 'w'),
    #     indent=3
    # )

    # anonymize AV dataset
    dataset = 'darkreddit_aa'
    train_stats, val_stats, test_stats = anonymize_authors_aa(
        PATHS[dataset]['train'], 
        PATHS[dataset]['val'], 
        PATHS[dataset]['test']
    )
    json.dump(
        [train_stats, val_stats, test_stats],
        open(os.path.join(os.path.dirname(PATHS[dataset]['train']), 'dataset_stats.json'), 'w'),
        indent=3
    )

    # sanity checks
    # get_av_dataset_stats("/darkweb/darknet_authorship_verification/agora/darknet_authorship_verification_train.json")
    # get_av_dataset_stats("/darkweb/darknet_authorship_verification/agora/darknet_authorship_verification_val.json")
    # get_av_dataset_stats("/darkweb/darknet_authorship_verification/agora/darknet_authorship_verification_test.json")
    