import datetime
from scipy import optimize
import pandas as pd
import numpy as np


class XIRR():
    def __init__(self):
        self.guess_list = [x for x in np.arange(0.1, 1, 0.1) for x in (x, -x)]
        self.annualized_factor = 1 / 365.

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
        res = 0
        for t in chron_order:
            res += t[1] / (1 + rate) ** ((t[0] - t0).days * self.annualized_factor)
        return res

    def eir_derivative_func(self, rate, cash_flow):
        """Find the derivative or the EIR function, used for calculating
        Newton's method:

        http://en.wikipedia.org/wiki/Newton's_method

        EIR = cf*(1+rate)^d
        f'rate = cf*d*(rate+1)^(d-1)

        Credit: http://mail.scipy.org/pipermail/numpy-discussion/2009-May/042736.html
        """
        # pmts, dates = [x[1] for x in cash_flow], [x[0] for x in cash_flow]

        dcf = 0
        for i, val in enumerate(cash_flow):  # cf
            d = val[0] - cash_flow[0][0]
            n = (-d.days * self.annualized_factor)
            dcf += val[1] * n * (rate + 1) ** (n - 1)
        return dcf

    def eir_second_derivative_func(self, rate, cash_flow):
        """
        similar to first derivative
        """
        # pmts, dates = [x[1] for x in cash_flow], [x[0] for x in cash_flow]
        dcf = 0
        for i, val in enumerate(cash_flow):  # cf
            d = val[0] - cash_flow[0][0]
            n = (-d.days * self.annualized_factor)
            dcf += val[1] * n * (n - 1) * (rate + 1) ** (n - 2)
        return dcf

    def xirr(self, cashflows):

        """
        Calculate the Internal Rate of Return of a series of cashflows at irregular intervals.

        :param cashflows: the pair (date, cash_flow),
               the list is assumed to sorted by date in ascending order, i.e. cashflows[0] is the inital cash flow
               Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.

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
        unique_sign_non_zero = set(list(filter(lambda i: i != 0, sign_list)))

        if len(unique_sign_non_zero) < 2:
            return np.nan

        o = []
        for i in self.guess_list:
            if len(o) == 1:
                return o[0] if ~isinstance(o[0], complex) else np.nan
            else:
                try:
                    o.append(optimize.newton(lambda r: self.xnpv(r, cashflows), i,
                                             fprime=lambda r: self.eir_derivative_func(r, cashflows),
                                             fprime2=lambda r: self.eir_second_derivative_func(r, cashflows)
                                             # ,
                                             # rtol=0.00001
                                             ))
                except:
                    pass


def get_look_back_quarter_date(current_date: datetime.date,
                               lb_months: int):
    """

    :param current_date: dateimte.date
    :param lb_period: if look back, negatvie, otherwise, positive
    :return:
    """
    return (current_date + pd.offsets.MonthEnd(lb_months)).date()


def get_turnover_standard(group, portfolio_value, purchase_col=['new_add_cash_flow'], sold_col=['new_exit_cash_flow']):
    # Portfolio value is the end value of the portfolio
    new_add_cash_flow = (group[purchase_col].sum(axis=1)).sum()
    new_exit_cash_flow = (group[sold_col].sum(axis=1)).sum()
    # portfolio_value = group.portfolio_value.median()
    return (min([new_add_cash_flow if new_add_cash_flow > 0 else np.inf,
                 new_exit_cash_flow if new_exit_cash_flow > 0 else np.inf]) if max(
        [new_add_cash_flow, new_exit_cash_flow]) > 0 else 0) / portfolio_value \
        if portfolio_value > 0 \
        else np.nan


if __name__ == '__main__':
    pass
    positive_cash_flow = np.random.uniform(0, 100000, 10)
    negative_cash_flow = np.random.uniform(-100000, 0, 10)
    cash_flows = [negative_cash_flow[0],
                  *np.random.choice([*positive_cash_flow, *negative_cash_flow[1:]], 19, replace=False)]
    dates = [x.date() for x in pd.date_range(datetime.date(2018, 9, 30), datetime.date(2019, 9, 30), periods=20)]
    cash_flow_list = [(d, v) for d, v in zip(dates, cash_flows)]

    xsd = XIRR()
    irr = xsd.xirr(cash_flow_list)
    pd.DataFrame(cash_flow_list).to_csv('t.csv', index=False)
