from math import exp,log

def design(lead,hands,combined):
    base=(1,1-min(lead,6)/6)
    return base+(int(hands),) if combined else base

def predict(coef,x):
    linear=sum(c*v for c,v in zip(coef,x))
    return 1/(1+exp(-linear))

def fit(rows,combined):
    weights=[0.]*(3 if combined else 2)
    points=[(design(r["lead"],r["hands_busy"],combined),r["missed"]) for r in rows]
    for _ in range(1200):
        residuals=[(x,predict(weights,x)-truth) for x,truth in points]
        gradient=[sum(x[i]*error for x,error in residuals)/len(points) for i in range(len(weights))]
        weights=[c-.6*(g+(.012*c if i else 0)) for i,(c,g) in enumerate(zip(weights,gradient))]
    return weights

def loss(coef,rows,combined):
    terms=[]
    for r in rows:
        value=predict(coef,design(r["lead"],r["hands_busy"],combined))
        selected=value if r["missed"] else (1-value)
        terms.append(-log(max(selected,1e-12)))
    return sum(terms)/len(terms)
