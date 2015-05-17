import theano
from theano import tensor as T
import numpy as np
import cPickle
from sklearn.manifold import TSNE
import pylab


#data
data = cPickle.load(open('data.pk', 'rb'))
trainx = data['train_inputs']
trainy = data['train_targets']
testx = data['test_inputs']
testy = data['test_targets']

#constants
vocab = data['vocab']
vocab_size = len(vocab)
context_len = 3
embed_dim = 16
num_hidden = 128   #change this later maybe
embed_layer_dim = context_len*embed_dim
batch_size = 20

#create some functions

def floatX(X):
    return np.asarray(X, dtype=theano.config.floatX)

def init_weights(shape):
    return theano.shared(floatX(np.random.randn(*shape) * 0.01))

def sgd(cost, params, lr=0.1):
    grads = T.grad(cost=cost, wrt=params)
    updates = []
    for p, g in zip(params, grads):
        updates.append([p, p - g * lr])
    return updates

def model(x, w_h, w_o):
    h = T.nnet.sigmoid(T.dot(x, w_h))
    pyx = T.nnet.softmax(T.dot(h, w_o))
    return pyx

#declare some variables that we will be using
idxs = T.imatrix()
y = T.ivector()

#we have to create the word embeddings here:
embeddings = np.asarray(np.random.randn(vocab_size, embed_dim), dtype=theano.config.floatX)
t_embeddings = theano.shared(embeddings)

x = t_embeddings[idxs].reshape((idxs.shape[0],embed_layer_dim))

w_h = init_weights((embed_layer_dim,num_hidden))
w_o = init_weights((num_hidden, vocab_size))

py_x = model(x, w_h, w_o)
y_x = T.argmax(py_x, axis=1)

cost = T.mean(T.nnet.categorical_crossentropy(py_x, y))
params = [t_embeddings,w_h, w_o]

updates = sgd(cost, params)

train = theano.function(inputs=[idxs, y], outputs=cost, updates=updates, allow_input_downcast=True)
predict = theano.function(inputs=[idxs], outputs=y_x, allow_input_downcast=True)

for i in range(100): #number of epochs
    for start, end in zip(range(0, len(trainx), batch_size), range(batch_size, len(trainx), batch_size)):
        cost = train(trainx[start:end], trainy[start:end])
    print np.mean(testy == predict(testx))

tsne_model = TSNE(n_components=2, random_state=0)
tsne_results = tsne_model.fit_transform(embeddings)


pylab.figure(figsize=(15,15))
for i, w in enumerate(vocab):
    pylab.text(tsne_results[i][0],tsne_results[i][1], w)
pylab.xlim(tsne_results[:, 0].min(), tsne_results[:, 0].max())
pylab.ylim(tsne_results[:, 1].min(), tsne_results[:, 1].max())

pylab.savefig('tsne_plot')

pylab.close()
