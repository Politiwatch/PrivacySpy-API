"""
PrivacySpy package containing helper methods and
the main functionality, including the extraction
and analysis of a privacy policy given its URL address.
"""
from goose3 import Goose
from flask import jsonify
import urllib
import spacy
import cld2
import json


class Spy:
    """
    Spy is the NLP backend used for PrivacySpy privacy
    policy analysis. Currently, it can analyze a sentence
    'importance' score. Later, it will support predicting
    whether some article is a privacy policy, and hopefully
    will be able to evaluate a privacy policy's OpenPD score.
    """
    __version__ = "1.0"

    def __init__(self):
        """
        Initializes PrivacySpy.

        Parameters
        ----------
        port: integer
            The port number for the server to run on

        TODO:
            - load the deep RNN model that classifies whether the main content
            at the URL is actually a privacy policy
        """
        self.goose = Goose()
        self.nlp = spacy.load('en_core_web_sm')
        with open("data/keyword_coefficients.json", 'r') as f:
            self.coefficients = json.load(f)

    @staticmethod
    def is_english(text):
        """
        Checks if the given string is English or not
        using CLD (Compact Language Detection).

        Returns
        -------
        bool:
            True if English, False otherwise
        """
        isReliable, _, details = cld2.detect(text)

        return isReliable != 0 and details[0][1] == "en"

    def extract_policy_from_url(self, url):
        """
        Uses Goose to extract the main content from
        the given URL -- usually, a privacy policy.

        Returns
        -------
        str:
            Cleaned text representation of the main content

        Raises exception if there was an error connecting
        to the URL or extracting the main content.
        """

        return self.goose.extract(url=url).cleaned_text

    @staticmethod
    def convertToUrlString(str):
        """
        Returns
        -------
        str:
            The string in application/x-www-form-urlencoded format
        """
        return urllib.parse.quote(str, safe='')

    @staticmethod
    def split_to_sentences(doc):
        """
        Parameters
        ----------
        spacy.tokens.doc.Doc:
            Privacy Policy as a SpaCy doc (created using `nlp(doc)`)

        Returns
        -------
        list:
            List of sentences in SpaCy sentence object format
        """
        return [sent for sent in doc.sents]

    @staticmethod
    def split_to_lemmas(sentences):
        """
        Parameters
        ----------
        spacy.tokens.doc.Doc.sents as a list:
            List of sentences as SpaCy sentence objects

        Returns
        -------
        List of sentences each split into a list of lemmatized words
        """
        return [[word.lemma_ for word in sentence if word.pos_ ==
                 'VERB' or word.pos_ == 'NOUN' or word.pos_ == 'PROPN']
                for sentence in sentences]

    @staticmethod
    def output(response, error=False, errorCode=0):
        """
        Returns
        -------
        JSON response in PrivacySpy format
        """
        obj = {
            "version": __version__,
            "response": response,
            "status": "success" if error == False else "error"
        }
        if errorCode != 0:
            obj["errorCode"] = errorCode

        return jsonify(obj)

    def sentence_score(self, sentence):
        """
        Parameters
        ----------
        list, str:
            list of sentence lemmas

        Returns
        -------
        float:
            sentence score, based on coefficients and sentence length
        """

        return (1 / len(sentence)) * sum([self.coefficients[word]
                                          for word in sentence if word in self.coefficients.keys()])

    def calculate_sentence_scores(self, sentences):
        """
        Generates a list of dictionaries each containing a sentence
        in string format and its score based on sentence_score method.
        """
        words = Spy.split_to_lemmas(sentences)

        scores = []
        max_score = 0
        for i, sentence in enumerate(words):
            score = self.sentence_score(sentence)
            if score > max_score:
                max_score = score
            scores.append({
                "sentence": sentences[i].text,
                "score": score
            })
            """
            raw_sentence = sentences[i].text
            for j, item in enumerate(raw_sentence.splitlines()):
                if j == 0:
                    scores.append({
                        "sentence": item,
                        "score": score
                    })
                else:
                    scores.append({
                        "sentence": item,
                        "score": 0
                    })
            """
        for item in scores:
            item["score"] /= max_score

        return scores

    def privacy_policy_summary(self, text):
        doc = self.nlp(text)

        sentences = Spy.split_to_sentences(doc)

        return self.calculate_sentence_scores(sentences)
