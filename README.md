# Linked-DocRED

Dataset, source code for the entity-linking annotation, the baseline and the metrics for the paper *"Linked-DocRED – Enhancing DocRED with Entity-Linking to Evaluate End-To-End Document-Level Information Extraction Pipelines"*.

The dataset is located in the [Linked-DocRED/ folder](Linked-DocRED/). We hope Linked-DocRED will participate in discovering and developing more performant IE pipelines.

*We also propose the alternative dataset Linked-Re-DocRED, located in the [Linked-Re-DocRED/ folder](Linked-Re-DocRED/). It is based on Re-DocRED *[[1]](#cite-1)*, which is an improved version of DocRED.*

## Introduction

Information Extraction (IE) pipelines aim to extract meaningful entities and relations from documents and structure them into a knowledge graph that can then be used in downstream applications. Training and evaluating such pipelines requires a dataset annotated with entities, coreferences, relations, and entity-linking. However, existing datasets either lack entity-linking labels, are too small, not diverse enough, or automatically annotated (that is, without a strong guarantee of the correction of annotations).

Therefore, we propose **Linked-DocRED**, to the best of our knowledge, the first manually-annotated, large-scale, document-level IE dataset.
We enhance the existing and widely-used DocRED *[[2]](#cite-2)* dataset with entity-linking labels that are generated thanks to a semi-automatic process that guarantees high-quality annotations. In particular, we use hyperlinks in Wikipedia articles to provide disambiguation candidates. *The dataset is located in the [Linked-DocRED folder](Linked-DocRED/). The source code for the disambiguation is accessible at [Disambiguation Process](entity-linking/)*.

We also propose a complete framework of metrics to benchmark end-to-end IE pipelines, and we define an entity-centric metric to evaluate entity-linking *(see [Metrics](metrics/))*.

The evaluation of a baseline shows promising results while highlighting the challenges of an end-to-end IE pipeline *(see [Baseline](baseline/))*.

## Table of contents

* [Linked-DocRED data and format](Linked-DocRED/)
* [Metrics](metrics/)
* [Baseline](baseline/)
* [DocRED disambiguation process](entity-linking/)

## License

Linked-DocRED, the source code for the baseline, the metrics, and the disambiguation process are licensed under the GPLv3 License. For more details, please refer to the [LICENSE.md file](LICENSE.md).

```
Linked-DocRED
Copyright (C) 2023 Alteca.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

## Contact

If you have questions using Linked-DocRED, please e-mail us at pygenest@alteca.fr.

## Citation

If you make use of Linked-DocRED or this code in your work, please kindly cite the following paper:

Genest, Pierre-Yves, Pierre-Edouard Portier, Előd Egyed-Zsigmond, and Martino Lovisetto. “Linked-DocRED – Enhancing DocRED with Entity-Linking to Evaluate End-To-End Document-Level Information Extraction Pipelines.” In <i>Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR’23)</i>, 11. Taipei, Taiwan: Association for Computing Machinery, 2023. <a href="https://doi.org/10.1145/3539618.3591912">https://doi.org/10.1145/3539618.3591912</a>.

```bibtex
@inproceedings{10.1145/3539618.3591912,
  title = {{Linked-DocRED – Enhancing DocRED with Entity-Linking to Evaluate End-To-End Document-Level Information Extraction Pipelines}},
  booktitle = {{Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR'23)}},
  author = {Genest, Pierre-Yves and Portier, Pierre-Edouard and Egyed-Zsigmond, El\"{o}d and Lovisetto, Martino},
  year = {2023},
  pages = {11},
  publisher = {{Association for Computing Machinery}},
  address = {{Taipei, Taiwan}},
  doi = {10.1145/3539618.3591912},
  isbn = {978-1-4503-9408-6},
}
```

## References

<div class="csl-entry"><a name="cite-1"></a><b>[1]</b>Tan, Qingyu, Lu Xu, Lidong Bing, Hwee Tou Ng, and Sharifah Mahani Aljunied. “Revisiting DocRED - Addressing the False Negative Problem in Relation Extraction.” In <i>Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing</i>, 8472–87. Abu Dhabi, United Arab Emirates: Association for Computational Linguistics, 2022. <a href="https://aclanthology.org/2022.emnlp-main.580">https://aclanthology.org/2022.emnlp-main.580</a>.</div>
<div class="csl-entry"><a name="cite-2"></a><b>[2]</b> Yao, Yuan, Deming Ye, Peng Li, Xu Han, Yankai Lin, Zhenghao Liu, Zhiyuan Liu, Lixin Huang, Jie Zhou, and Maosong Sun. “DocRED: A Large-Scale Document-Level Relation Extraction Dataset.” In <i>Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics</i>, 764–77. Florence, Italy: Association for Computational Linguistics, 2019. <a href="https://doi.org/10.18653/v1/p19-1074">https://doi.org/10.18653/v1/p19-1074</a>.</div>