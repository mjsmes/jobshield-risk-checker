# JobShield Evaluation

## Purpose
This directory contains a small synthetic dataset and a script for preliminary testing of the JobShield detection engine.

## Dataset
The dataset contains 10 manually written examples:
- 5 labelled scam
- 5 labelled legitimate

These examples are synthetic and have not been independently verified against real job advertisements.

## Running the evaluation
From the project root:

    python evaluation/evaluate.py

## Important limitations
The reported precision, recall, false-positive rate and accuracy describe only this small synthetic dataset. They must not be presented as verified real-world performance.

A detected warning signal does not automatically mean an advert is a scam. The current classification threshold is a score of 20 or higher.
