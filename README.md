# Program translation retrieval system
Program translation is a growing demand in software engineering. Manual program translation requires programming expertise in source and target language. One way to automate this process is to make use of the big data of programs. However, existing code retrieval techniques lack the design to cover cross-language code retrieval. Other data-driven approaches require human efforts in constructing cross-language parallel datasets to train translation models. We built a code translation retrieval system. We use a lightweight but informative program representation, which can be generalized to all imperative PLs. Furthermore, we implement our customized index structure and hierarchical filtering mechanism for efficient code retrieval from a big data.

![workflow](/images/workflow.png "workflow")

## Dependencies
- Python3
- MongoDB
- pymongo
- ANTLR (Java target)

## Create a feature database
In the offline phase, system constructs feature reapresentation for each program in the database and save it in a feature database for use.

`sh create_feature_db.sh path_to_your_database`

## Create index
System constructs path-type-bucket-index for the featrue representations. 

`python3 create_index.py`

User can specify maximum bucket size in `bucket_size.json`.

## Retrieve translation for a program
`sh translate.sh path_to_input_code target_language`

In this repository, we add 4 programming languages: Python, Java, C++, JavaScript. 

If you want more languages support, just simply run ANTLR parser in your desired language and enrich the `lang_collection` list in each file.

## Evaluations
### Comparison with Data-driven Program Translation
We compare the results of effectiveness and efficiency of our system with the following state-of-the-art baselines:
- 1pSMT: phrase-based SMT on sequential programs.
- mppSMT: multi-phase phrase-based SMT.
- Tree2tree: tree-to-tree neural networks.
- TransCoder: weakly-supervise translation model.

![eval1](/images/eval1.png )

### Comparison with Code Search Engines
We compare with two well-known code search engines:
- Sourcerer: This system is based on Lucene Core, which indexes code like natural text.
- CodeHow: We use CodeHow only to perform free-text queries over codebase and skip the process of API understanding as it requires external API documentations. 

To make the baselines comparable, we change their inputs to raw programs in source language, and run them to retrieve similar programs in target language. And to maintain the fairness of the experiment, we remove the parts of their systems that require user efforts.

![eval2](/images/eval2.png )

### Comparison with other Representations on a Large Real-world Dataset
The dataset used in this experiment is generated from the [Public Git Archive](https://github.com/src-d/datasets/tree/master/PublicGitArchive)~(PGA) - a database with more than 260,000 top bookmarked Git repositories from GitHub. The size of this dataset has reached 6TB. To save experiment equipment and time, under the premise of ensuring the validity of the experiment and the reproducibility of the data, we randomly sample a sufficiently large subset of this database. We choose the four programming languages with the most pushes on github - JavaScript, Python, Java, and C++. They are also representative of programming languages with different characteristics. Based on the number of stargazers, we pick 1% files in these four languages from PGA to be our raw dataset.

To show the advantage of our system, we compare its results to other representation methods:
- Our system: Our approach considers structural features, textual features and their dependency.
- Structural: Only the structural part of our approach.
- Textual: It extracts all the text from the program and uses BoW model to only construct representation for textual features. This is the common method used in cross language code clone detection. We implement a sliding window with a length of 20 tokens and compare the similarity of these token sequences.
- Structural+Textual: This representation is the combination of (2) and (3) without feature dependency.
- Our system(W2V): Same as (1) except changing the textual feature from BoW to W2V. We train cross language word vector on PGA database.
- Code2vec: The state-of-the-art code representation which transforms code syntax tree to a vector trained by neural network. For Java, we directly use the provided trained model to generate code vectors. For other languages, we train code vectors on PGA database. Then we determine the candidates by calculating the cosine similarity.

![eval3](/images/eval3.png )
