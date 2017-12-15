# bucketnet

This is a toy example of how LSTM can be used to generate music.

## Example results

Example .midi files converted directly from model's text output can be found in the `data/examples` directory.

## Dataset

For a sake of simplicity data used in training is in [.abc text music notation](http://abcnotation.com/wiki/abc:standard:v2.1).  The data used in this model's training can be acquired [here](https://github.com/adactio/TheSession-data).

## How to play with it

If you would like only to see what the model is capable of, use `compose.py`. In this file you can tell the trained model to continue any input fragment of a song in .abc format or feed it nothing and see what it will come up with.

If you would like to train your own model, because you want it to learn on a different kind of music, use `train.py`. There you can change filtering parameters for tunes and model's build and training parameters. If you want to switch the dataset altogether, you will have to fiddle around a little bit with the processing package as it is tailored to the specific .csv row format from TheSession's tunes collection.
