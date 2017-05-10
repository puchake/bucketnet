# bucketnet

It's music generating RNN inspired by [this](http://karpathy.github.io/2015/05/21/rnn-effectiveness/) great article and comments under it. **Work in progress.**

## Model

### Network

Network will be contructed out of stacked LSTM layers. Rest will probably change as I will experiment with the network more, so I can't write much more about it.

### Input

Single note, which is given as an input to the network is composed of several one-hot parts representing its parameters. 

Both duration and delta time (time passed from a start of a previous note) of a note are given as vectors of 11 elements, 2 of which are set to 1. First 8 elements encode time interval. Only one of those elements is set to 1 and it represents whether an interval lasts a full, half, quarter, eighth, sixteenth, 1/32nd, 1/64th note or is immediate (has no duration). Next 3 elements contain the type of the interval:
- normal - duration or delta time is exactly what is kept in the first part of the time vector,
- dotted - like in a dotted note the real interval is 1.5 times longer than what is encoded in first 8 elements of the time vector,
- triplet - base interval is modified like in a triplet note (2/3 * base interval).

Note's pitch representation depends on whether the whole note vector is supposed to contain a guitar or drums note. For drums notes it is simply one-hot vector which encodes one of the percussion sounds (snare, low tom etc. - only 26 typical sounds are recognized) or a pause. For guitar it is a little bit more complicated as the whole vector, which is 19 elements long, contains 2 one-hot parts: one which encodes one out of six recognized octaves and other for 12 possible octave pitches + 1 special pause pitch.

### Output

Output is in the same format as input.

### Loss function

Output vector is compared with the next input vector. Loss derived from that comparison is a sum of softmax-crossentropy classification losses for each one-hot part of compared vectors.

## Data

Data collection is still in progress. I plan to use mainly Buckethead songs as data source for now. It isn't only because I like the pieces of this particular artist's music. They are also basically only instrumental pieces with great variety of complexity, so basing RNN on them may produce interesting results. I'm using all sorts of playable guitar (drums too) tab files of chosen songs, which i convert first to midi files. Then i use conversion script to transform the midi file into set of note vectors.
