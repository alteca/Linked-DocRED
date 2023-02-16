# Baseline

This folder contains the definition of the PNA (PURE, NeuralCoref, ATLOP) + entity-linking baseline proposed along with Linked-DocRED.

The user shall execute the modules in the following order:
* [PURE](pure/) (Named Entity Recognition),
* [NeuralCoref](neuralcoref/) (Coreference Resolution),
* [ATLOP](atlop/) (Relation Extraction),
* [Entity-Linking](entity-linking/).

*Warning: Each module has its own Python version and environment. The user shall install each environment separately.*