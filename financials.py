import datetime
from scipy import optimize
import pandas as pd
import numpy as np

class xirr_second_derivative():
    def __init__(self):
        self.guess_list = [x for x in np.arange(0.1, 1, 0.1) for x in (x, -x)]

    def xnpv(self, rate, cashflows):
        """
        Calculate the net present value of a series of cashflows at irregular intervals.
        Arguments
        ---------
        * rate: the discount rate to be applied to the cash flows
        * cashflows: a list object in which each element is a tuple of the form (date, amount),
         where date is a python datetime.date object and amount is an integer or floating point number.
         Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.

        Returns
        -------
        * returns a single value which is the NPV of the given cash flows.
        Notes
        ---------------
        * The Net Present Value is the sum of each of cash flows discounted back to the date of the first cash flow.
        The discounted value of a given cash flow is A/(1+r)**(t-t0), where A is the amount, r is the discout rate,
        and (t-t0) is the time in years from the date of the first cash flow in the series (t0) to the date of
        the cash flow being added to the sum (t).

        * This function is equivalent to the Microsoft Excel function of the same name.
        """
        chron_order = sorted(cashflows, key=lambda x: x[0])
        t0 = chron_order[0][0]  # t0 is the date of the first cash flow
        return sum([t[1] / (1 + rate) ** ((t[0] - t0).days / 365.0) for t in chron_order])

    def eir_derivative_func(self, rate, cash_flow):
        """Find the derivative or the EIR function, used for calculating
        Newton's method:

        http://en.wikipedia.org/wiki/Newton's_method

        EIR = cf*(1+rate)^d
        f'rate = cf*d*(rate+1)^(d-1)

        Credit: http://mail.scipy.org/pipermail/numpy-discussion/2009-May/042736.html
        """
        pmts, dates = [x[1] for x in cash_flow], [x[0] for x in cash_flow]

        dcf = []
        for i, cf in enumerate(pmts):
            d = dates[i] - dates[0]
            n = (-d.days / 365.)
            dcf.append(cf * n * (rate + 1) ** (n - 1))
        return sum(dcf)

    def eir_second_derivative_func(self, rate, cash_flow):
        """
        similar to first derivative
        """
        pmts, dates = [x[1] for x in cash_flow], [x[0] for x in cash_flow]

        dcf = []
        for i, cf in enumerate(pmts):
            d = dates[i] - dates[0]
            n = (-d.days / 365.)
            dcf.append(cf * n * (n-1) * (rate + 1) ** (n - 2))
        return sum(dcf)

    def xirr(self, cashflows):

        """
        :param cashflows: the list is assumed to sorted by date in asending order, i.e. cashflows[0] is the inital cash flow

        Calculate the Internal Rate of Return of a series of cashflows at irregular intervals.
        Arguments
        ---------
        * cashflows: a list object in which each element is a list of the pair (date, cash_flow),
        where date is a python datetime.date object and cash_flow is an integer or floating number.
        Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
        * guess (optional, default = 0.1): a guess at the solution to be used as a starting point for the numerical solution.
        Returns
        --------
        * Returns the IRR as a single value

        Notes
        ----------------
        * The Internal Rate of Return (IRR) is the discount rate at which the Net Present Value (NPV)
        of a series of cash flows is equal to zero.
        The NPV of the series of cash flows is determined using the xnpv function in this module.
        The discount rate at which NPV equals zero is found using the secant method of numerical solution.
        * This function is equivalent to the Microsoft Excel function of the same name.

        """
        if len(cashflows) < 2:
            return np.nan

        sign_list = list(np.sign([x[1] for x in cashflows]))
        unique_sign_non_zero = dict.fromkeys([i for i in sign_list if i!=0])

        if len(unique_sign_non_zero)<2:
            return np.nan

        try:
            # print(cashflows)
            o = []
            for i in self.guess_list:
                try:
                    if len(o) == 1:
                        return o[0] if ~isinstance(o[0], complex) else np.nan
                    else:
                        print(i)
                        o.append(optimize.newton(lambda r: self.xnpv(r, cashflows), i,
                                                 fprime= lambda r: self.eir_derivative_func(r, cashflows),
                                                 fprime2= lambda r : self.eir_second_derivative_func(r, cashflows)
                                                 # ,
                                                 # rtol=0.00001
                        ))
                except:
                    pass
        except:
            return np.nan


def get_look_back_quarter_date(current_date: datetime.date,
                               lb_months: int):
    """

    :param current_date: dateimte.date
    :param lb_period: if look back, negatvie, otherwise, positive
    :return:
    """
    return (current_date + pd.offsets.MonthEnd(lb_months)).date()

def get_turnover_standard(group, portfolio_value, purchase_col = ['new_add_cash_flow'], sold_col = ['new_exit_cash_flow']):
    #Portfolio value is the end value of the portfolio
    new_add_cash_flow = (group[purchase_col].sum(axis = 1)).sum()
    new_exit_cash_flow = (group[sold_col].sum(axis = 1)).sum()
    # portfolio_value = group.portfolio_value.median()
    return (min([new_add_cash_flow if new_add_cash_flow > 0 else np.inf,
                      new_exit_cash_flow if new_exit_cash_flow > 0 else np.inf]) if max([new_add_cash_flow, new_exit_cash_flow]) > 0 else 0 )/portfolio_value \
           if portfolio_value > 0 \
           else np.nan


if __name__ == '__main__':
    pass
    cash_flow= [-2246618000,  -0, -221098065.3, -119790087.1, 2761567298]
    date = [x.date() for x in pd.date_range(datetime.date(2018,9,30), datetime.date(2019,9,30), periods = 5)]
    cash_flow_list = [[d, v] for d,v in zip(date, cash_flow)]


    xsd = xirr_second_derivative()
    t = xsd.xirr(cash_flow_list)

    
