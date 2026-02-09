from afinn import Afinn

afinn_en = Afinn(language="en")
afinn_da = Afinn(language="da")

def sentiment(text: str) -> str:
    score_en = afinn_en.score(text)
    score_da = afinn_da.score(text)

    score = score_en if abs(score_en) > abs(score_da) else score_da

    if score > 0:
        return "positive"
    elif score < 0:
        return "negative"
    else:
        return "neutral"