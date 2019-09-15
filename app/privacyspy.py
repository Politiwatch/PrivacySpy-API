"""
PrivacySpy package containing helper methods and
the main functionality, including the extraction
and analysis of a privacy policy given its URL address.
"""
from goose3 import Goose
from flask import jsonify
import urllib
import spacy
from langdetect import detect
import json
from readability import Document
import requests
from bs4 import BeautifulSoup


class Spy:
    """
    Spy is the NLP backend used for PrivacySpy privacy
    policy analysis. Currently, it can analyze a sentence
    'importance' score. Later, it will support predicting
    whether some article is a privacy policy, and hopefully
    will be able to evaluate a privacy policy's OpenPD score.
    """
    __version__ = "1.1"

    def __init__(self, coefs_path="./data/keyword_coefficients.json"):
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
        self.nlp = spacy.load('en_core_web_sm')
        with open(coefs_path, 'r') as f:
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

        try:
            return detect(text) == "en"
        except:
            return False

    def extract_policy_from_url(self, url):
        """
        Uses "readability-lxml" to extract the main content from
        the given URL -- usually, a privacy policy.

        Returns
        -------
        str:
            Cleaned text representation of the main content

        Raises exception if there was an error connecting
        to the URL or extracting the main content.
        """
        text = requests.get(url).text
        return self.extract_policy_from_html(text, url=url)

    def extract_policy_from_html(self, html, url=None):
        """
        Uses "readability-lxml" to extract the main content from
        the given HTML -- usually, from a page with a 
        privacy policy.

        Returns
        -------
        str:
            Cleaned text representation of the main content

        Raises exception if there was an error connecting
        to the URL or extracting the main content.
        """
        doc = Document(html, url=url)
        soup = BeautifulSoup(doc.summary(), "html5lib")
        for img in soup.find_all("img"):
            _ = img.extract()
        for tag in soup():
            for attribute in ["class", "id", "name", "style"]:
                del tag[attribute]
        return soup.prettify()

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

    def lemmatize(self, text):
        words = []
        doc = self.nlp(text)
        for sentence in doc.sents:
            words.extend([word.lemma_.lower() for word in sentence if word.pos_ ==
                 'VERB' or word.pos_ == 'NOUN' or word.pos_ == 'PROPN'])
        return words

    def split_to_lemmas(self, sentences):
        """
        Parameters
        ----------
        spacy.tokens.doc.Doc.sents as a list:
            List of sentences as SpaCy sentence objects

        Returns
        -------
        List of sentences each split into a list of lemmatized words
        """
        return [[word.lemma_.lower() for word in sentence if word.pos_ ==
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
            "version": Spy.__version__,
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
        if len(sentence) == 0:
            return 0
        else:
            return (1 / len(sentence)) * sum([self.coefficients[word]
                                              for word in sentence if word in self.coefficients.keys()])

    def calculate_sentence_scores(self, sentences):
        """
        Generates a list of dictionaries each containing a sentence
        in string format and its score based on sentence_score method.
        """
        words = self.split_to_lemmas(sentences)

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
        for item in scores:
            item["score"] /= max_score

        return scores

    def privacy_policy_summary(self, html):
        if "<p" in html: # without closing > to allow for classes
            soup = BeautifulSoup(html, 'html5lib')
            for p in soup.find_all(["p", "li"]):
                text = self.lemmatize(p.get_text())
                score = self.sentence_score(text)
                p["data-score"] = score
            for a in soup.find_all("a"):
                a["rel"] = "nofollow"
            body = " ".join(str(t) for t in soup.find("body").contents)
            return body # no score scaling
        else:
            # todo: test heavily
            doc = self.nlp(BeautifulSoup(html, 'html5lib').get_text())
            sentences = self.split_to_sentences(doc)
            return " ".join(["<span data-score='%s'>%s</span>" % (sentence["score"], sentence["sentence"].replace("\n", "<br>")) for sentence in self.calculate_sentence_scores(sentences)])
