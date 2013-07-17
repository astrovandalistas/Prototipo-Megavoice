#! /usr/bin/python

# -*- coding: utf-8 -*-

from nltk.corpus import cess_esp, brown
from nltk import UnigramTagger, BigramTagger
from cPickle import dump

# read corpus
corpusEs = cess_esp.tagged_sents()
corpusEn = brown.tagged_sents()

# Train the unigram taggers
uniTagEs = UnigramTagger(corpusEs)
uniTagEn = UnigramTagger(corpusEn)

# write out files
outputEs = open('uniTag.es.pkl', 'wb')
outputEn = open('uniTag.en.pkl', 'wb')
dump(uniTagEs, outputEs, -1)
dump(uniTagEn, outputEn, -1)
outputEs.close()
outputEn.close()
