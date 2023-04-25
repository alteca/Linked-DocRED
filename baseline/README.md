# Baseline

This folder contains the definition of the PNA (PURE, NeuralCoref, ATLOP) + entity-linking baseline proposed along with Linked-DocRED.

The user shall execute the modules in the following order:
* [PURE](pure/) [[1]](#cite-1) (Named Entity Recognition),
* [NeuralCoref](neuralcoref/) (Coreference Resolution),
* [ATLOP](atlop/) [[2]](#cite-2) (Relation Extraction),
* [Entity-Linking](entity-linking/).

*Warning: Each module has its own Python version and environment. The user should install each environment separately.*

## References

<div class="csl-entry"><a name="cite-1"></a><b>[1]</b> Zhong, Zexuan, and Danqi Chen. “A Frustratingly Easy Approach for Entity and Relation Extraction.” In <i>Proceedings of the 2021 Annual Conference of the North American Chapter of the Association for Computational Linguistics</i>, 50–61. Online: Association for Computational Linguistics, 2021. <a href="https://doi.org/10.18653/v1/2021.naacl-main.5">https://doi.org/10.18653/v1/2021.naacl-main.5</a>.</div>

<div class="csl-entry"><a name="cite-2"></a><b>[2]</b> Zhou, Wenxuan, Kevin Huang, Tengyu Ma, and Jing Huang. “Document-Level Relation Extraction with Adaptive Thresholding and Localized Context Pooling.” In <i>Proceedings of the AAAI Conference on Artificial Intelligence</i>, 35:14612–20. Online: AAAI Press, 2021. <a href="https://doi.org/10.1609/aaai.v35i16.17717">https://doi.org/10.1609/aaai.v35i16.17717</a>.</div>