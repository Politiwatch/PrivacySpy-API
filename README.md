# PrivacySpy API
The repository contains the source code powering the API service of PrivacySpy. It is used for text highlighting based on an individual sentence's importance (assuming the sentence is a part of a privacy policy). `Dockerfile` is included.

## Installation
Before proceeding, make sure you have Python 3.6 installed.
```
pip install -r requirements.txt
pip install -U spacy==2.0.3
python3 -m spacy download en
python3 -m spacy download xx
```

## Docker Build
```
docker build -t privacyspy-api .
docker run -p 80:80 -t privacyspy-api
```

## API endpoints
`/analyze`

Parameters:

- `url` - URL of a privacy policy in `application/x-www-form-urlencoded` format
- `token` - PrivacySpy token that corresponds to the environment variable token of the service

Returns:

In case of success, the API endpoint returns a JSON object of the following format:

```
{
  "response": [
    {
      "score": 0.554556940669308, 
      "sentence": "What do we mean by \"personal information?\""
    }, 
    {
      "score": 0.8253833221800004, 
      "sentence": "For us, \"personal information\" means information which identifies you, like your name or email address."
    }, ...
  ], 
  "status": "success", 
  "version": "1.0"
}
```
If there was an error, `status` will contain `error`, and the response will contain the error message instead. Additionally, there will be an `error_code` field containing integer values corresponding to the error as follows:
- `1` -- no URL provided
- `2` -- no token provided
- `3` -- invalid token
- `4` -- failed to extract content from the url
- `5` -- privacy policy is not in English