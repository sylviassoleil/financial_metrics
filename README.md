# financial metrics

### Implementation of XIRR with `scipy.newton`
because the function is convex 
using Newton’s Method for gradient descend (including the secondary derivative of cost function)



### Example
```

positive_cash_flow = np.random.uniform(0, 100000, 10)
negative_cash_flow = np.random.uniform(-100000, 0, 10)
cash_flows = [negative_cash_flow[0], *np.random.choice([*positive_cash_flow, *negative_cash_flow[1:]], 19, replace=False)]
dates = [x.date() for x in pd.date_range(datetime.date(2018, 9, 30), datetime.date(2019, 9, 30), periods=20)]
cash_flow_list = [(d, v) for d, v in zip(dates, cash_flows)]

xsd = XIRR()
irr = xsd.xirr(cash_flow_list)
```


### Error Handlings & Potential Issues

- if only negative (and zero) cashflows, return None 
- the intermediate calculations can involve complex numbers as the (1+return_rate) could be negative, some warnings will be flagged.
