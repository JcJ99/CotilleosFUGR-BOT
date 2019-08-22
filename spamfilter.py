from Auths import ibm_key, ibm_language_url
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, KeywordsOptions
import json

negative_limit = -0.8

text_understanding = NaturalLanguageUnderstandingV1(
	version = "2019-07-12",
	iam_apikey = ibm_key,
	url = ibm_language_url
)

def is_inapropiate(text, lang="es"):
	response = text_understanding.analyze(
		text = text,
		language = lang,
		features = Features(sentiment=SentimentOptions(document=True))
	).get_result()
	sentiment = response["sentiment"]["document"]["score"]
	if sentiment <= negative_limit:
		return (True, sentiment)
	else: return (False, sentiment)

	
if __name__ == "__main__":
	text = input("Introduce texto: ")
	print(is_inapropiate(text)[1])