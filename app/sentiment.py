from afinn import Afinn

afinn = Afinn()

def sentiment(text: str) -> str:
    score = afinn.score(text)
    if score > 0:
        return "positive"
    elif score < 0:
        return "negative"
    else:
        return "neutral"
